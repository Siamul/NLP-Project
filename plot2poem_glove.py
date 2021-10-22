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

glove_model_name = 'glove.840B.300d.txt'

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

import spacy
from annoy import AnnoyIndex
import numpy as numpy

nlp =  spacy.load("en_core_web_lg")

titles = plotutils.titleindex()
plots = plotutils.loadplots()

def getplot(idx):
    return idx, titles[idx], plots[idx]
def pickrandomplot():
    idx = random.randrange(len(titles))
    return getplot(idx)
def getplotfromtitle(title):
    idx = titles.index(title)
    return getplot(idx)

title2idx = dict([(t, i) for i, t in enumerate(titles)])

glove_vectors = {}
print("Loading GloVe model: ", glove_model_name)
with tqdm(total=os.path.getsize(glove_model_name)) as pbar:
    with open(glove_model_name, 'r', encoding='utf-8') as glove_vec_file:
        for line in glove_vec_file:
            pbar.update(len(line))
            values = line.split(' ')
            glove_vectors[values[0]] = np.asarray(values[1:], dtype='float32')

keywords = True
if keywords:
    k_tag = 'keywords_'
else:
    k_tag = ''

def line_vector(line):
    line = line.strip()
    exclude = list(string.punctuation)
    line = ''.join([ch for ch in line if ch not in exclude])
    s = nlp(line)
    if keywords:
        s = [word for word in s if word.pos_ in ('NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN', 'ADP')]
    vecs = [glove_vectors[word.text.lower()] for word in s if word.text.lower() in glove_vectors.keys()]
    if len(vecs) == 0:
        #print(line)
        return None
    else:
        return np.array(vecs).mean(axis=0)

#print(line_vector('this is a test').shape)
#print(line_vector('this is a much larger test because it is needed, really really needed').shape)
if not os.path.exists(k_tag + 'poetry_annoy_' + glove_model_name.split('.')[0] + '_' + glove_model_name.split('.')[1] +'.ann'):
    t = AnnoyIndex(300, metric='angular')   #fast nearest neight lookup for poem lines
    all_lines = []
    print('Building annoy for fast nearest neighbor search...', ' with keywords...' if keywords else '')
    with tqdm(total=os.path.getsize('poetry.txt')) as pbar:
        with open('poetry.txt', 'r', encoding='utf-8') as poetry_file:
            i = 0
            j = 0
            for line in poetry_file:
                j += 1
                pbar.update(len(line))
                line_vec = line_vector(line)
                if line_vec is not None:
                    t.add_item(i, line_vec)
                    all_lines.append(line.strip())
                    i += 1

    t.build(50)  # build 50 trees. More trees gives higher precision when querying
    t.save(k_tag + 'poetry_annoy_' + glove_model_name.split('.')[0] + '_' + glove_model_name.split('.')[1] +'.ann')
    print('Saved Poetry annoy model. Poetry lines kept: ', i, ', Poetry lines discarded: ', j - i)
    with open(k_tag + 'poetry_' + glove_model_name.split('.')[0] + '_' + glove_model_name.split('.')[1] + '.txt', 'w', encoding='utf-8') as poetry_file:
        for line in all_lines:
            poetry_file.write(line +'\n')
else:
    print('Loading previously made annoy model and poetry lines', 'based on keywords.' if keywords else '')
    t = AnnoyIndex(300, metric='angular')
    t.load(k_tag + 'poetry_annoy_' + glove_model_name.split('.')[0] + '_' + glove_model_name.split('.')[1] +'.ann')
    with open(k_tag + 'poetry_' + glove_model_name.split('.')[0] + '_' + glove_model_name.split('.')[1] + '.txt', 'r', encoding='utf-8') as poetry_file:
        all_lines = poetry_file.readlines()

all_lines = [line.strip() for line in all_lines]
assert(t.get_n_items() == len(all_lines))

_, title, sentences = getplotfromtitle('Shrek') #pickrandomplot() for randomly picking a plot
print(title)
print("".join([sentence for sentence in sentences.split('\n')]))

print('##########################################################################')

# convert a plot to poetry without rhythmic constraint
plot_sentences = sentences.split('\n')
plot_sentences = filter(None, plot_sentences)
plot_sentences = [sentence.strip() for sentence in plot_sentences if sentence.strip()]
for sentence in plot_sentences:
    sent_vec = line_vector(sentence)
    if sent_vec is None:
        print('The sentence for empty vector is: ', sentence)
        continue
    match_idx = t.get_nns_by_vector(sent_vec, n=100)[0]
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
    #print(src_words[-1].lower())
    word_rhymes = pronouncing.rhymes(src_words[-1].lower())
    matched_lines = []
    for line in all_lines:
        line = line.strip()
        exclude = list(string.punctuation)
        line = ''.join([ch for ch in line if ch not in exclude])
        words = filter(None, line.split(' '))
        words = [word for word in words]
        #print(words[-1].lower())
        if words[-1].lower() in word_rhymes:
            matched_lines.append(line)
    return matched_lines


def find_closest(src_line, lines):
    
    src_vec = line_vector(src_line)
    vec_lines = [line_vector(line) for line in lines]
    index = 0
    while(vec_lines[index] is None):
        index += 1
    best_dist = angular_distance(src_vec, vec_lines[index])
    best_index = index
    for i in range(index+1, len(vec_lines)):
        if vec_lines[i] is not None:
            dist = angular_distance(src_vec, vec_lines[i])
            if dist < best_dist:
                best_dist = dist
                best_index = i
    
    return lines[best_index], best_dist

even = (len(plot_sentences) % 2 == 0)

for i in range(1, len(plot_sentences) - 1, 2):
    sentence1 = plot_sentences[i-1]
    sentence2 = plot_sentences[i]
    s1_vec = line_vector(sentence1)
    s2_vec = line_vector(sentence2)
    match_idx_s1 = t.get_nns_by_vector(s1_vec, n=100)[0]
    match_idx_s2 = t.get_nns_by_vector(s2_vec, n=100)[0]

    # Find closest poetry line to first line
    m1_poetry_line_1 = all_lines[match_idx_s1]
    poetry_match1_vec = line_vector(m1_poetry_line_1)
    m1_dist1 = angular_distance(s1_vec, poetry_match1_vec)

    # Get closest rhyming line according to first match
    rhyming_lines_m1 = find_rhyming_lines(m1_poetry_line_1)
    if len(rhyming_lines_m1) > 0:
        m1_poetry_line_2, m1_dist2 = find_closest(sentence2, rhyming_lines_m1)
    else:
        m1_poetry_line_2 = ""
        m1_dist2 = inf

    # Find closest poetry line to second line
    m2_poetry_line_2 = all_lines[match_idx_s2]
    poetry_match2_vec = line_vector(m2_poetry_line_2)
    m2_dist2 = angular_distance(s2_vec, poetry_match2_vec)

    # Get closest rhyming line according to second match
    rhyming_lines_m2 = find_rhyming_lines(m2_poetry_line_2)
    if len(rhyming_lines_m2) > 0:
        m2_poetry_line_1, m2_dist1 = find_closest(sentence1, rhyming_lines_m2)
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
    sent_vec = line_vector(last_sentence)
    match_idx = t.get_nns_by_vector(sent_vec, n=100)[0]
    print('-----------------------------------------------')
    print(last_sentence)
    print('v')
    print(all_lines[match_idx])
    print('-----------------------------------------------')