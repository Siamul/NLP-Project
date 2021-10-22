# Some parts of the code are taken from https://github.com/aparrish/plot-to-poem/ 
# The poetry corpus is taken from https://github.com/aparrish/gutenberg-poetry-corpus

import random
import sys
import plotutils
import poemutils
import pronouncing
import re
import string
import sklearn
from math import sqrt, acos, pi, inf
import numpy as np
from tqdm import tqdm
import os
from sentence_transformers import SentenceTransformer
import _pickle as pickle

model_name = sys.argv[1]
model = SentenceTransformer(model_name, device='cuda' if torch.cuda.is_available() else 'cpu')

def cos_sim(u, v):
    dot = np.sum(u * v)
    l2u = sqrt(np.sum(u * u))
    l2v = sqrt(np.sum(v * v))
    cs = dot/(l2u * l2v)
    cs = cs if cs > -1 else -1
    cs = cs if cs < 1 else 1
    return cs

def angular_distance(u, v):
    return acos(cos_sim(u, v)) / pi

from annoy import AnnoyIndex
import numpy as numpy

print("Loading plots....")
titles = plotutils.titleindex()
plots = plotutils.loadplots()

#def line_vector(line):
#    return model.encode(line)

#print(line_vector('this is a test').shape)
#print(line_vector('this is a much larger test because it is needed, really really needed').shape)

    
all_lines = []
print("Loading poetry... ")
with open('poetry.txt', 'r', encoding='utf-8') as poetry_file:
    for line in poetry_file:
        all_lines.append(line.strip())
        
if not os.path.exists(model_name + '_poetry_bert_embeddings.pkl'):              
    print("Finding BERT embeddings for poetry")
    poetry_embeddings = model.encode(all_lines, convert_to_numpy=True, show_progress_bar=True)#, batch_size=16)
    with open(model_name + '_poetry_bert_embeddings.pkl', 'wb') as poebefile:
        pickle.dump(poetry_embeddings, poebefile, protocol=4)
else:
    print("Loading pre-calculated BERT embeddings for poetry")
    with open(model_name + '_poetry_bert_embeddings.pkl', 'rb') as poebefile:
        poetry_embeddings = pickle.load(poebefile)

if not os.path.exists(model_name + '_plot_bert_embeddings.pkl'):    
    print("Finding BERT embeddings for plots")
    plots_embeddings = []
    all_plot_sentences = []
    all_plot_lengths = [0]
    sum_len_plot_sen = 0
    for i in tqdm(range(len(plots))):
        plot_sentences = plots[i].split('\n')
        plot_sentences = filter(None, plot_sentences)
        plot_sentences = [sentence.strip() for sentence in plot_sentences if sentence.strip()]
        all_plot_sentences += plot_sentences
        sum_len_plot_sen += len(plot_sentences)
        all_plot_lengths.append(sum_len_plot_sen)
    print(len(all_plot_sentences))
    print(all_plot_lengths[-1])  
    all_plot_line_embeddings = model.encode(all_plot_sentences, convert_to_numpy=True, show_progress_bar=True)
    for i in range(len(all_plot_lengths)-1):
        plots_embeddings.append(all_plot_line_embeddings[all_plot_lengths[i]:all_plot_lengths[i+1]])
    #    plots_embeddings.append(plot_line_embeddings)
    with open(model_name + '_plot_bert_embeddings.pkl', 'wb') as plobefile:
        pickle.dump(plots_embeddings, plobefile, protocol=4)
else:
    print("Loading pre-calculated BERT embeddings for plots")
    with open(model_name + '_plot_bert_embeddings.pkl', 'rb') as plobefile:
        plots_embeddings = pickle.load(plobefile)
    
if not os.path.exists(model_name + '_poetry_annoy_bert.ann'):
    t = AnnoyIndex(1024, metric='angular')   #fast nearest neight lookup for poem lines
    print('Building annoy for fast nearest neighbor search...')
    for i in tqdm(range(len(poetry_embeddings))):
        t.add_item(i, poetry_embeddings[i])
    t.build(100)  # build 100 trees. More trees gives higher precision when querying
    t.save(model_name + '_poetry_annoy_bert.ann')
    print('Saved Poetry annoy model based on BERT.')
else:
    print('Loading previously made annoy model')
    t = AnnoyIndex(1024, metric='angular')
    t.load(model_name + '_poetry_annoy_bert.ann')
    
assert(t.get_n_items() == len(all_lines))

def getplot(idx):
    plot_sentences = plots[idx].split('\n')
    plot_sentences = filter(None, plot_sentences)
    plot_sentences = [sentence.strip() for sentence in plot_sentences if sentence.strip()]
    return idx, titles[idx], plot_sentences, plots_embeddings[idx]
    
def pickrandomplot():
    idx = random.randrange(len(titles))
    return getplot(idx)
    
def getplotfromtitle(title):
    idx = title2idx[title]
    return getplot(idx)

title2idx = dict([(t, i) for i, t in enumerate(titles)])

_, title, plot_sentences, plot_embeddings = getplotfromtitle('Shrek') #pickrandomplot() for randomly picking a plot
print(title)
print("".join([sentence for sentence in plot_sentences]))

print('##########################################################################')

# convert a plot to poetry without rhythmic constraint

for i in range(len(plot_sentences)):
    sentence = plot_sentences[i]
    sent_vec = plot_embeddings[i]
    match_idx = t.get_nns_by_vector(sent_vec, n=1000)[0]
    print('-----------------------------------------------')
    print(sentence)
    print('v')
    print(all_lines[match_idx])
    print('-----------------------------------------------')

print('##########################################################################')

# convert a plot to poetry with pairs of rhythmic sentences
def find_rhyming_lines(src_text):
    src_text = src_text.strip()
    exclude = list(string.punctuation)
    src_text = ''.join([ch for ch in src_text if ch not in exclude])
    src_words = filter(None, src_text.split(' '))
    src_words = [word for word in src_words]
    #print(src_words)
    #print(src_words[-1].lower())
    word_rhymes = pronouncing.rhymes(src_words[-1].lower())
    #print(word_rhymes)
    matched_lines = []
    for i in range(len(all_lines)):
        line = all_lines[i]
        line = line.strip()
        exclude = list(string.punctuation)
        line = ''.join([ch for ch in line if ch not in exclude])
        words = filter(None, line.split(' '))
        words = [word for word in words]
        if len(words) == 0:
            continue
        #print(words[-1].lower())
        if words[-1].lower() in word_rhymes:
            matched_lines.append([line, poetry_embeddings[i]])
    return matched_lines


def find_closest(src_vec, linevectuples):
    
    vec_lines = [linevectuple[1] for linevectuple in linevectuples]
    index = 0
    while (vec_lines[index] is None):
        index += 1
    best_dist = angular_distance(src_vec, vec_lines[index])
    best_index = index
    for i in range(index+1, len(vec_lines)):
        if vec_lines[i] is not None:
            dist = angular_distance(src_vec, vec_lines[i])
            if dist < best_dist:
                best_dist = dist
                best_index = i
    
    return linevectuples[best_index][0], best_dist

even = (len(plot_sentences) % 2 == 0)

for i in range(1, len(plot_sentences) - 1, 2):
    sentence1 = plot_sentences[i-1]
    sentence2 = plot_sentences[i]
    s1_vec = plot_embeddings[i-1]
    s2_vec = plot_embeddings[i]
    match_idx_s1 = t.get_nns_by_vector(s1_vec, n=1000)[0]
    match_idx_s2 = t.get_nns_by_vector(s2_vec, n=1000)[0]

    # Find closest poetry line to first line
    m1_poetry_line_1 = all_lines[match_idx_s1]
    poetry_match1_vec = poetry_embeddings[match_idx_s1]  #line_vector(m1_poetry_line_1)
    m1_dist1 = angular_distance(s1_vec, poetry_match1_vec)

    # Get closest rhyming line according to first match
    rhyming_lines_m1 = find_rhyming_lines(m1_poetry_line_1)
    if len(rhyming_lines_m1) > 0:
        m1_poetry_line_2, m1_dist2 = find_closest(s2_vec, rhyming_lines_m1)
    else:
        m1_poetry_line_2 = ""
        m1_dist2 = inf

    # Find closest poetry line to second line
    m2_poetry_line_2 = all_lines[match_idx_s2]
    poetry_match2_vec = poetry_embeddings[match_idx_s2]
    m2_dist2 = angular_distance(s2_vec, poetry_match2_vec)

    # Get closest rhyming line according to second match
    rhyming_lines_m2 = find_rhyming_lines(m2_poetry_line_2)
    if len(rhyming_lines_m2) > 0:
        m2_poetry_line_1, m2_dist1 = find_closest(s1_vec, rhyming_lines_m2)
    else:
        if len(rhyming_lines_m1) == 0:
            print('-----------------------------------------------')
            print(sentence1)
            print(sentence2)
            print('v')
            print(all_lines[match_idx_s1])
            print(all_lines[match_idx_s2])
            print('-----------------------------------------------')
            continue
        else:
            m2_poetry_line_1 = ""
            m2_dist1 = inf

    # Take the closest overall 
    if m1_dist1 + m1_dist2 <= m2_dist1 + m2_dist2:
        print('-----------------------------------------------')
        print(sentence1)
        print(sentence2)
        print('v')
        print(m1_poetry_line_1)
        print(m1_poetry_line_2)
        print('-----------------------------------------------')
    else:
        print('-----------------------------------------------')
        print(sentence1)
        print(sentence2)
        print('v')
        print(m2_poetry_line_1)
        print(m2_poetry_line_2)
        print('-----------------------------------------------')
        

if not even:
    last_sentence = plot_sentences[-1]
    sent_vec = plot_embeddings[-1]
    match_idx = t.get_nns_by_vector(sent_vec, n=1000)[0]
    print('-----------------------------------------------')
    print(last_sentence)
    print('v')
    print(all_lines[match_idx])
    print('-----------------------------------------------')
