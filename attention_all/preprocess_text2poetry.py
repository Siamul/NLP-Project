''' Handling the data io '''
import os
import argparse
import logging
import _pickle as pickle
import urllib
from tqdm import tqdm
import sys
import codecs
import spacy
import torch
import tarfile
import torchtext.legacy.data as torchtextdata
from torchtext.legacy.data import Field, BucketIterator, TabularDataset
import torchtext.legacy.datasets as torchtextdatasets
import transformer.Constants as Constants
from learn_bpe import learn_bpe
from apply_bpe import BPE
import torchtext
import torch
from torchtext.data.utils import get_tokenizer
from collections import Counter
from torchtext.vocab import Vocab
import io
import pandas as pd
from sklearn.model_selection import train_test_split


class TqdmUpTo(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def file_exist(dir_name, file_name):
    for sub_dir, _, files in os.walk(dir_name):
        if file_name in files:
            return os.path.join(sub_dir, file_name)
    return None

def compile_files(raw_dir, raw_files, prefix):
    src_fpath = os.path.join(raw_dir, f"raw-{prefix}.src")
    trg_fpath = os.path.join(raw_dir, f"raw-{prefix}.trg")

    if os.path.isfile(src_fpath) and os.path.isfile(trg_fpath):
        sys.stderr.write(f"Merged files found, skip the merging process.\n")
        return src_fpath, trg_fpath

    sys.stderr.write(f"Merge files into two files: {src_fpath} and {trg_fpath}.\n")

    with open(src_fpath, 'w') as src_outf, open(trg_fpath, 'w') as trg_outf:
        for src_inf, trg_inf in zip(raw_files['src'], raw_files['trg']):
            sys.stderr.write(f'  Input files: \n'\
                    f'    - SRC: {src_inf}, and\n' \
                    f'    - TRG: {trg_inf}.\n')
            with open(src_inf, newline='\n') as src_inf, open(trg_inf, newline='\n') as trg_inf:
                cntr = 0
                for i, line in enumerate(src_inf):
                    cntr += 1
                    src_outf.write(line.replace('\r', ' ').strip() + '\n')
                for j, line in enumerate(trg_inf):
                    cntr -= 1
                    trg_outf.write(line.replace('\r', ' ').strip() + '\n')
                assert cntr == 0, 'Number of lines in two files are inconsistent.'
    return src_fpath, trg_fpath


def encode_file(bpe, in_file, out_file):
    sys.stderr.write(f"Read raw content from {in_file} and \n"\
            f"Write encoded content to {out_file}\n")
    
    with codecs.open(in_file, encoding='utf-8') as in_f:
        with codecs.open(out_file, 'w', encoding='utf-8') as out_f:
            for line in in_f:
                out_f.write(bpe.process_line(line))


def encode_files(bpe, src_in_file, trg_in_file, data_dir, prefix):
    src_out_file = os.path.join(data_dir, f"{prefix}.src")
    trg_out_file = os.path.join(data_dir, f"{prefix}.trg")

    if os.path.isfile(src_out_file) and os.path.isfile(trg_out_file):
        sys.stderr.write(f"Encoded files found, skip the encoding process ...\n")

    encode_file(bpe, src_in_file, src_out_file)
    encode_file(bpe, trg_in_file, trg_out_file)
    return src_out_file, trg_out_file
    
'''
def data_process(filepaths, vocab, tokenizer):
    raw_prosaic_iter = iter(io.open(filepaths[0], encoding="utf8"))
    raw_poetry_iter = iter(io.open(filepaths[1], encoding="utf8"))
    data = []
    for (raw_prosaic, raw_poetry) in zip(raw_prosaic_iter, raw_poetry_iter):
        prosaic_tensor_ = torch.tensor([vocab[token] for token in tokenizer(raw_prosaic)],
                                dtype=torch.long)
        poetry_tensor_ = torch.tensor([vocab[token] for token in en_tokenizer(raw_poetry)],
                                dtype=torch.long)
        data.append((prosaic_tensor_, poetry_tensor_))
    return data
    
def build_vocab(filepaths, tokenizer):
    counter = Counter()
    with io.open(filepaths[0], encoding="utf8") as f:
        for string_ in f:
            counter.update(tokenizer(string_))
    with io.open(filepaths[1], encoding="utf8") as f:
        for string_ in f:
            counter.update(tokenizer(string_))
    return Vocab(counter, specials=['<unk>', '<pad>', '<bos>', '<eos>'])
'''

def create_json_csv_from_text(filepaths):
    print('Creating json and csv from txt data')
    prosaic_text = open(filepaths[0], 'r', encoding='utf-8').read().split('\n')
    poetry_text = open(filepaths[1], 'r', encoding='utf-8').read().split('\n')
    raw_data = {'src': prosaic_text, 'trg': poetry_text}
    df = pd.DataFrame(raw_data, columns = ['src', 'trg'])
    train, val_test = train_test_split(df, test_size=0.1)
    val, test = train_test_split(val_test, test_size=0.5)

    train.to_json('prosaic2poetry-train.json', orient='records', lines=True) 
    train.to_csv('prosaic2poetry-train.csv', index=False)
    val.to_json('prosaic2poetry-val.json', orient='records', lines=True) 
    val.to_csv('prosaic2poetry-val.csv', index=False)
    test.to_json('prosaic2poetry-test.json', orient='records', lines=True) 
    test.to_csv('prosaic2poetry-test.csv', index=False)
    
    
    

def main():
    '''
    Usage: python preprocess.py -lang_src de -lang_trg en -save_data multi30k_de_en.pkl -share_vocab
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-save_data', type=str, default='./glove_840B_aligned_data.pkl')
    parser.add_argument('-data_src', type=str, default='../glove_840B_aligned_plot_nonrhythm.txt')
    parser.add_argument('-data_trg', type=str, default='../glove_840B_aligned_poetry_nonrhythm.txt')
    
    parser.add_argument('-max_len', type=int, default=510)
    parser.add_argument('-min_word_count', type=int, default=3)
    parser.add_argument('-keep_case', action='store_true')
    parser.add_argument('-share_vocab', action='store_true')
    #parser.add_argument('-ratio', '--train_valid_test_ratio', type=int, nargs=3, metavar=(8,1,1))
    #parser.add_argument('-vocab', default=None)

    opt = parser.parse_args()
    #assert not any([opt.data_src, opt.data_trg]), 'Custom data input is not support now.'
    #assert not any([opt.data_src, opt.data_trg]) or all([opt.data_src, opt.data_trg])
    #print(opt)
    
    

    lang_model = spacy.load('en_core_web_lg')

    def tokenize(text):
        return [tok.text for tok in lang_model.tokenizer(text)]

    SRC = Field(
        tokenize=tokenize, lower=not opt.keep_case,
        pad_token=Constants.PAD_WORD, init_token=Constants.BOS_WORD, eos_token=Constants.EOS_WORD)

    TRG = Field(
        tokenize=tokenize, lower=not opt.keep_case,
        pad_token=Constants.PAD_WORD, init_token=Constants.BOS_WORD, eos_token=Constants.EOS_WORD)

    MAX_LEN = opt.max_len
    MIN_FREQ = opt.min_word_count

    def filter_examples_with_length(x):
        return len(vars(x)['src']) <= MAX_LEN and len(vars(x)['trg']) <= MAX_LEN
        
    if not os.path.exists('prosaic2poetry-train.json'):
        create_json_csv_from_text([opt.data_src, opt.data_trg])
    
    
    train, val, test = TabularDataset.splits(
        path='',
        train='prosaic2poetry-train.json',
        validation='prosaic2poetry-val.json',
        test='prosaic2poetry-test.json',
        format='json',
        fields={'src': ('src', SRC), 'trg': ('trg', TRG)} ,
        filter_pred=filter_examples_with_length
        )
            
    '''
    train, val, test = torchtext.datasets.Multi30k.splits(
            exts = ('.prosaic.poetry'),
            fields = (SRC, TRG),
            filter_pred=filter_examples_with_length)
    
    '''
    
    SRC.build_vocab(train.src, min_freq=MIN_FREQ)
    print('[Info] Get source language vocabulary size:', len(SRC.vocab))
    TRG.build_vocab(train.trg, min_freq=MIN_FREQ)
    print('[Info] Get target language vocabulary size:', len(TRG.vocab))
    
    
    print('[Info] Merging two vocabulary ...')
    for w, _ in SRC.vocab.stoi.items():
        # TODO: Also update the `freq`, although it is not likely to be used.
        if w not in TRG.vocab.stoi:
            TRG.vocab.stoi[w] = len(TRG.vocab.stoi)
    TRG.vocab.itos = [None] * len(TRG.vocab.stoi)
    for w, i in TRG.vocab.stoi.items():
        TRG.vocab.itos[i] = w
    SRC.vocab.stoi = TRG.vocab.stoi
    SRC.vocab.itos = TRG.vocab.itos
    print('[Info] Get merged vocabulary size:', len(TRG.vocab))
    

    data = {
        'settings': opt,
        'vocab': {'src': SRC, 'trg': TRG},
        'train': train.examples,
        'valid': val.examples,
        'test': test.examples}
        
    print('[Info] Dumping the processed data to pickle file', opt.save_data)
    with open(opt.save_data, 'wb') as dataFile
        pickle.dump(data, dataFile, protocol=4)


if __name__ == '__main__':
    main()
    #main()
