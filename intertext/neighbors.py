import argparse
import os
import sys
import re

import random
random.seed(1001)

import numpy as np

import torch
torch.manual_seed(1001)
try:
    torch.cuda.manual_seed(1001)
except:
    print('no NVIDIA driver found')

import torch.nn as nn

from seqmod.modules.lm import LM
from seqmod import utils as u
from seqmod.misc.optimizer import Optimizer
from seqmod.misc.dataset import Dict, BlockDataset

from utils import load_data
from train import (make_lm_check_hook, make_lm_save_hook,
                   save_model, load_from_file)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_path',
                        help=('Path to pretrained model.'))
    parser.add_argument('--corpus', type=str, default='data/asimov',
                        help='Path to dir with input files')
    parser.add_argument('--load_data', action='store_true',
                        help=('Whether to load a preprocessed corpus. ' +
                              'Requires DATA_PATH.'))
    parser.add_argument('--save_data', action='store_true',
                        help=('Save npy corpus file and Dict. ' +
                              'Requires DICT_PATH and DATA_PATH'))
    parser.add_argument('--dict_path', type=str)
    parser.add_argument('--data_path', type=str)
    parser.add_argument('--filter_file', type=str, default=None)
    parser.add_argument('--skip_head_lines', default=20, type=int,
                        help='Ignore first n lines of a file.')
    parser.add_argument('--skip_tail_lines', default=20, type=int,
                        help='Ignore last n lines of a file.')
    args = parser.parse_args()
    model, d, data = None, None, None

    assert args.model_path, "MODEL_PATH required"
    print(f'Args: {args}')

    model = u.load_model(args.model_path)
    d, model, old_args = model['dict'], model['model'], model['train_params']

    # copy unaltered train vars from model
    for v in 'cell layers hid_dim emb_dim bptt level'.split():
        args.__dict__[v] = old_args[v]

    if args.gpu:
        model.cuda()

    print(model)
    print('* number of parameters: %d' % model.n_params())

    novel_path = '/home/mike/weasimov_data/05token/Dan Brown - 4. De Da Vinci code.txt'
    orig_sentences = [s.strip() for s in open(novel_path, 'r')]

    X = []
    for inp_sent in inp_data:
        inp_ints = np.array(d.transform(inp_sent), dtype=np.int32)
        inp_data = torch.LongTensor(inp_ints.astype(np.int64))
        X.append(get_hidden(model, [inp]))

    X = np.array(X, dtype=np.float32)

    from sklearn.neighbors import KNeighborsClassifier
    knn = KNeighborsClassifier(n_neighbors=5,
                               algorithm='brute',
                               metric='cosine')

    knn.fit(X, range(len(X)))
    neighbor_dist, neighbor_idxs = knn.kneighbors(X=X_train,
                                                  n_neighbors=5,
                                                  return_distance=True)
    for sentence, dist, idxs in zip(neighbor_dist, neighbor_idxs):
        print('-> input:', sentence)
        for d, idx in zip(dist, idxs):
            print('\t+', d, ':', orig_sentences[idx])


def get_hidden(model, inp):
    emb = model.embeddings(inp)
    outs, hidden = model.rnn(emb, model.init_hidden_for(emb))
    return outs  # outs is same as before (seq_len, batch, hidden_size)


if __name__ == '__main__':
    main()
