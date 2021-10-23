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

    t.build(100)  # build 100 trees. More trees gives higher precision when querying
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

def getplot(idx):
    plot_sentences = plots[idx].split('\n')
    plot_sentences = filter(None, plot_sentences)
    plot_sentences = [sentence.strip() for sentence in plot_sentences if sentence.strip()]
    return idx, titles[idx], plot_sentences
    
def pickrandomplot():
    idx = random.randrange(len(titles))
    return getplot(idx)
    
def getplotfromtitle(title):
    idx = title2idx[title]
    return getplot(idx)

title2idx = dict([(t, i) for i, t in enumerate(titles)])

print('##########################################################################')

# convert a plot to poetry without rhythmic constraint using multiprocessing

def process_plot_nonrhythm(idx):
    _, title, plot_sentences = getplot(idx)
    filtered_sentences = []
    poetry_sentences = []
    for sentence in plot_sentences:
        sent_vec = line_vector(sentence)
        if sent_vec is None:
            print('The sentence for empty vector is: ', sentence)
            continue
        match_idx = t.get_nns_by_vector(sent_vec, n=1000)[0]
        filtered_sentences.append(sentence)
        poetry_sentences.append(all_lines[match_idx])
    print('For Non-Rhythmic, Done ', title)
    return filtered_sentences, poetry_sentences

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
        if len(words) == 0:
            continue
        #print(words[-1].lower())
        if words[-1].lower() in word_rhymes:
            matched_lines.append(line)
    return matched_lines


def find_closest(src_line, lines):
    
    src_vec = line_vector(src_line)
    vec_lines = [line_vector(line) for line in lines]
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
    
    return lines[best_index], best_dist

def process_plot_rhythm(idx):

    _, title, plot_sentences = getplot(idx)
    filtered_sentences = []
    poetry_sentences = []

    index = 1
    while(index < len(plot_sentences)):
        sentence1 = plot_sentences[index-1]
        sentence2 = plot_sentences[index]

        s1_vec = line_vector(sentence1)
        s2_vec = line_vector(sentence2)

        if s1_vec is None:
            index += 1
            continue

        index += 2
        
        match_idx_s1 = t.get_nns_by_vector(s1_vec, n=1000)[0]
        
        if s2_vec is None:
            filtered_sentences.append(sentence1)
            poetry_sentences.append(all_lines[match_idx_s1])
            continue
                
        match_idx_s2 = t.get_nns_by_vector(s2_vec, n=1000)[0]

        filtered_sentences.append(sentence1)
        filtered_sentences.append(sentence2)

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
            sent_vec = line_vector(last_sentence)
            if sent_vec is not None:
                match_idx = t.get_nns_by_vector(sent_vec, n=1000)[0]
                filtered_sentences.append(last_sentence)
                poetry_sentences.append(all_lines[match_idx])
                filtered_sentences.append(last_sentence)
                poetry_sentences.append(all_lines[match_idx])
    print('For Rhythmic, Done ', title)
    return filtered_sentences, poetry_sentences

from multiprocessing import Pool
pool = Pool(processes=8)
print('Processing non-rhythmic.')
plot2poemdata = pool.map(process_plot_nonrhythm, range(len(titles)))
pool.close()
pool.join()
print('Done processing non-rhythmic, saving the dataset...')
with open(glove_model_name.split('.')[0] + '_' + glove_model_name.split('.')[1] +'_aligned_plot_nonrhythm.txt', 'a', encoding='utf-8') as plotFile:
     with open(glove_model_name.split('.')[0] + '_' + glove_model_name.split('.')[1] +'_aligned_poetry_nonrhythm.txt', 'a', encoding='utf-8') as poetryFile:    
        for plot, poem in plot2poemdata:
            for plot_line in plot:
                plotFile.write(plot_line + '\n')
            for poem_line in poem:
                poetryFile.write(poem_line + '\n')

print('Processing rhythmic.')
pool2 = Pool(processes=8)
plot2poemdatarhythmic = pool2.map(process_plot_rhythm, range(len(titles)))
pool2.close()
pool2.join()
print('Done processing rhythmic, saving the dataset...')
with open(glove_model_name.split('.')[0] + '_' + glove_model_name.split('.')[1] +'_aligned_plot_rhythm.txt', 'a', encoding='utf-8') as plotFile:
     with open(glove_model_name.split('.')[0] + '_' + glove_model_name.split('.')[1] +'_aligned_poetry_rhythm.txt', 'a', encoding='utf-8') as poetryFile:    
        for plot, poem in plot2poemdatarhythmic:
            for plot_line in plot:
                plotFile.write(plot_line + '\n')
            for poem_line in poem:
                poetryFile.write(poem_line + '\n')