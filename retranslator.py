from deep_translator import (GoogleTranslator,
                             MicrosoftTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             PapagoTranslator,
                             DeepL,
                             QCRI,
                             single_detection,
                             batch_detection)
                             
from tqdm import tqdm
import os
import sys

try:
    show = sys.argv[1]
except:
    show = None
    pass

iters = 5

def save_txt(text, filename):
    with open(filename, 'w') as filehandle:
        for line in text:
            filehandle.write(text+'\n')
    return True

if not os.path.exists('results/'):
    os.mkdir('results/')

# Google iterations
batch_size = 1024
txt_pre = 'results/detext'
file_en = '../poetry.txt'
for iter_no in tqdm(range(iters)):
    print("#####################################################")
    with open(file_en, 'r') as engFile:
        i = 0
        batch = []
        for line in tqdm(engFile, total=3085116):
            i += 1
            if i < batch_size:
                batch.append(line)
            else:
                de_lines = GoogleTranslator(source='english', target='german').translate_batch(batch)
                if show:
                    print('\n'.join(de_lines))
                en_lines = GoogleTranslator(source='german', target='english').translate_batch(de_lines)
                if show:
                    print('\n'.join(en_lines))
                txtFile = open(txt_pre+str(iter_no)+'.txt', 'a+')
                if en_lines is not None:
                    for en_line in en_lines:
                        txtFile.write(en_line + '\n')
                txtFile.close()
                i = 0
                batch = []
        if len(batch) > 0:
            de_lines = GoogleTranslator(source='english', target='german').translate_batch(batch)
            if show:
                print('\n'.join(de_lines))
            en_lines = GoogleTranslator(source='german', target='english').translate_batch(de_lines)
            if show:
                print('\n'.join(en_lines))
            txtFile = open(txt_pre+str(iter_no)+'.txt', 'a+')
            if en_lines is not None:
                for en_line in en_lines:
                    txtFile.write(en_line + '\n')
            txtFile.close()
            i = 0
            batch = []
    file_en = txt_pre+str(iter_no)+'.txt'
            
    
txt_pre = 'results/frtext'
file_en = '../poetry.txt'
for iter_no in tqdm(range(iters)):
    print("#####################################################")
    with open(file_en, 'r') as engFile:
        i = 0
        batch = []
        for line in tqdm(engFile, total=3085116):
            i += 1
            if i < batch_size:
                batch.append(line)
            else:
                fr_lines = GoogleTranslator(source='english', target='french').translate_batch(batch)
                if show:
                    print('\n'.join(fr_lines))
                en_lines = GoogleTranslator(source='french', target='english').translate_batch(fr_lines)
                if show:
                    print('\n'.join(en_lines))
                txtFile = open(txt_pre+str(iter_no)+'.txt', 'a+')
                if en_lines is not None:
                    for en_line in en_lines:
                        txtFile.write(en_line + '\n')
                txtFile.close()
                i = 0
                batch = []
                
        if len(batch) > 0:
            fr_lines = GoogleTranslator(source='english', target='french').translate_batch(batch)
            if show:
                print('\n'.join(fr_lines))
            en_lines = GoogleTranslator(source='french', target='english').translate_batch(fr_lines)
            if show:
                print('\n'.join(en_lines))
            txtFile = open(txt_pre+str(iter_no)+'.txt', 'a+')
            if en_lines is not None:
                for en_line in en_lines:
                    txtFile.write(en_line + '\n')
            txtFile.close()
            i = 0
            batch=[]
            
    file_en = txt_pre+str(iter_no)+'.txt'

    
    
    
