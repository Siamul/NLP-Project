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
import sys

model_name = sys.argv[1] # all-mpnet-base-v2
no_of_pool = int(sys.argv[2])

#model = SentenceTransformer('stsb-roberta-large', device='cuda')
model = SentenceTransformer(model_name, device='cuda')

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
    print("Finding ", model_name, " embeddings for poetry")
    poetry_embeddings = model.encode(all_lines, convert_to_numpy=True, show_progress_bar=True)#, batch_size=16)
    with open(model_name + '_poetry_bert_embeddings.pkl', 'wb') as poebefile:
        pickle.dump(poetry_embeddings, poebefile, protocol=4)
else:
    print("Loading pre-calculated ", model_name, " embeddings for poetry")
    with open(model_name + '_poetry_bert_embeddings.pkl', 'rb') as poebefile:
        poetry_embeddings = pickle.load(poebefile)

if not os.path.exists(model_name + '_plot_bert_embeddings.pkl'):    
    print("Finding ", model_name, " embeddings for plots")
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
    print("Loading pre-calculated ", model_name, " embeddings for plots")
    with open(model_name + '_plot_bert_embeddings.pkl', 'rb') as plobefile:
        plots_embeddings = pickle.load(plobefile)
    
if not os.path.exists('poetry_annoy_bert.ann'):
    t = AnnoyIndex(1024, metric='angular')   #fast nearest neight lookup for poem lines
    print('Building annoy for fast nearest neighbor search...')
    for i in tqdm(range(len(poetry_embeddings))):
        t.add_item(i, poetry_embeddings[i])
    t.build(100)  # build 100 trees. More trees gives higher precision when querying
    t.save(model_name + '_poetry_annoy_bert.ann')
    print('Saved Poetry annoy model based on ', model_name)
else:
    print('Loading previously made annoy model for ', model_name)
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

# create an aligned dataset with and without rhythmic constraint using multiprocessing

def process_plot_nonrhythm(idx):
    _, title, plot_sentences, plot_embeddings = getplot(idx)
    filtered_sentences = []
    poetry_sentences = []
    for i in range(len(plot_sentences)):
        sentence = plot_sentences[i]
        sent_vec = plot_embeddings[i]
        match_idx = t.get_nns_by_vector(sent_vec, n=1000)[0]
        filtered_sentences.append(sentence)
        poetry_sentences.append(all_lines[match_idx])
    print('For Non-Rhythmic, Done ', title)
    return filtered_sentences, poetry_sentences
    
def find_rhyming_lines(src_text):
    src_text = src_text.strip()
    exclude = list(string.punctuation)
    src_text = ''.join([ch for ch in src_text if ch not in exclude])
    src_words = filter(None, src_text.split(' '))
    src_words = [word for word in src_words]
    #print(src_words[-1].lower())
    word_rhymes = pronouncing.rhymes(src_words[-1].lower())
    matched_lines = []
    for i in range(len(all_lines)):
        line = all_lines[i]
        line = line.strip()
        if len(line) == 0:
            continue
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
    
    vec_lines = [vec for line, vec in linevectuples]
    best_dist = angular_distance(src_vec, vec_lines[0])
    best_index = 0
    for i in range(1, len(vec_lines)):
        dist = angular_distance(src_vec, vec_lines[i])
        if dist < best_dist:
            best_dist = dist
            best_index = i
    
    return linevectuples[best_index][0], best_dist


def process_plot_rhythm(idx):

    _, title, plot_sentences, plot_embeddings = getplot(idx)
    filtered_sentences = []
    poetry_sentences = []
    index = 1
    while(index < len(plot_sentences)):
        sentence1 = plot_sentences[index-1]
        sentence2 = plot_sentences[index]

        s1_vec = plot_embeddings[index-1]
        s2_vec = plot_embeddings[index]

        index += 2
        
        match_idx_s1 = t.get_nns_by_vector(s1_vec, n=1000)[0]                
        match_idx_s2 = t.get_nns_by_vector(s2_vec, n=1000)[0]

        filtered_sentences.append(sentence1)
        filtered_sentences.append(sentence2)

        # Find closest poetry line to first line
        m1_poetry_line_1 = all_lines[match_idx_s1]
        poetry_match1_vec = poetry_embeddings[match_idx_s1]
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
                poetry_sentences.append(all_lines[match_idx_s1])
                poetry_sentences.append(all_lines[match_idx_s2])
                continue
            else:
                m2_poetry_line_1 = ""
                m2_dist1 = inf

        # Take the closest overall 
        if m1_dist1 + m1_dist2 <= m2_dist1 + m2_dist2:
            poetry_sentences.append(m1_poetry_line_1)
            poetry_sentences.append(m1_poetry_line_2)
        else:
            poetry_sentences.append(m2_poetry_line_1)
            poetry_sentences.append(m2_poetry_line_2)
        
        if index == len(plot_sentences):
            last_sentence = plot_sentences[-1]
            sent_vec = plot_embeddings[-1]
            match_idx = t.get_nns_by_vector(sent_vec, n=1000)[0]
            filtered_sentences.append(last_sentence)
            poetry_sentences.append(all_lines[match_idx])
            filtered_sentences.append(last_sentence)
            poetry_sentences.append(all_lines[match_idx])
    print('For Rhythmic, Done ', title)
    return filtered_sentences, poetry_sentences
    
from multiprocessing import Pool

pool1 = Pool(processes=no_of_pool)
plot2poemdata = pool1.map(process_plot_nonrhythm, range(len(titles)))
pool1.close()
pool1.join()
with open(model_name + '_aligned_plot_nonrhythm.txt', 'a', encoding='utf-8') as plotFile:
     with open(model_name + '_aligned_poetry_nonrhythm.txt', 'a', encoding='utf-8') as poetryFile:    
        for plot, poem in plot2poemdata:
            for plot_line in plot:
                plotFile.write(plot_line + '\n')
            for poem_line in poem:
                poetryFile.write(poem_line + '\n')


pool2 = Pool(processes=no_of_pool)
plot2poemdatarhythmic = pool2.map(process_plot_rhythm, range(len(titles)))
pool2.close()
pool2.join()
with open(model_name + '_aligned_plot_rhythm.txt', 'a', encoding='utf-8') as plotFile:
     with open(model_name + '_aligned_poetry_rhythm.txt', 'a', encoding='utf-8') as poetryFile:    
        for plot, poem in plot2poemdatarhythmic:
            for plot_line in plot:
                plotFile.write(plot_line + '\n')
            for poem_line in poem:
                poetryFile.write(poem_line + '\n')
