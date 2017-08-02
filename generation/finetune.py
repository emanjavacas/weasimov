
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

from seqmod.misc.trainer import LMTrainer
from seqmod.misc.loggers import StdLogger, VisdomLogger
from loggers import CSVLogger
from seqmod.misc.optimizer import Optimizer
from seqmod.misc.dataset import Dict, BlockDataset
from seqmod.misc.early_stopping import EarlyStopping

from utils import load_data
from train import (make_lm_check_hook, make_lm_save_hook,
                  save_model, load_from_file)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_path',
                        help=('Path to pretrained model.'))

    # dataset
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
    parser.add_argument('--dev_split', default=0.01, type=float)
    parser.add_argument('--test_split', default=0.05, type=float)
    # training
    parser.add_argument('--epochs', default=10, type=int)
    parser.add_argument('--batch_size', default=464, type=int)
    parser.add_argument('--bptt', default=250, type=int)
    parser.add_argument('--dropout', default=.3, type=float)
    parser.add_argument('--gpu', action='store_true')
    # - optimizer
    parser.add_argument('--optim', default='Adam', type=str)
    parser.add_argument('--learning_rate', default=0.01, type=float)
    parser.add_argument('--learning_rate_decay', default=0.5, type=float)
    parser.add_argument('--start_decay_at', default=5, type=int)
    parser.add_argument('--decay_every', default=1, type=int)
    parser.add_argument('--max_grad_norm', default=5., type=float)
    parser.add_argument('--early_stopping', default=-1, type=int)
    # - check
    parser.add_argument('--seed', default=None)
    parser.add_argument('--decoding_method', default='sample')
    parser.add_argument('--max_seq_len', default=50, type=int)
    parser.add_argument('--temperature', default=.5, type=float)
    parser.add_argument('--checkpoint', default=100, type=int)
    parser.add_argument('--hooks_per_epoch', default=200, type=int)
    parser.add_argument('--saves_per_epoch', default=200, type=int)
    parser.add_argument('--log_checkpoints', action='store_true')
    parser.add_argument('--visdom_server', default='localhost')
    parser.add_argument('--save', action='store_true')
    parser.add_argument('--prefix', default='post', type=str)

    # logger
    parser.add_argument('--csv', type=str, default=' ')
    parser.add_argument('--note', type=str, default=" ", nargs='+')

    args = parser.parse_args()
    model, d, data = None, None, None

    assert args.model_path, "MODEL_PATH required"

    # make sure not to overwrite existing model:
    old_prefix = os.path.basename(args.model_path).split('.')[0]
    if old_prefix == args.prefix:
        print('Warning: prefix equal to existing prefix. Appending "-post".')
        args.prefix = args.prefix + '-post'

    model = u.load_model(args.model_path)
    d, model, old_args = model['dict'], model['model'], model['train_params']

    # copy unaltered train vars from model
    for v in 'cell layers hid_dim emb_dim bptt level'.split():
        args.__dict__[v] = old_args[v]

    # prepare data
    if args.load_data:
        print("Loading preprocessed datasets...")
        assert args.dict_path, "Processed data requires DICT_PATH"
        data = load_from_file(args.data_path, filter_file=args.filter_file)
    else:
        print("Transforming data...")
        print(args.filter_file)
        data = d.transform(
            load_data(path=args.corpus, level=args.level,
                      filter_file=args.filter_file,
                      skip_head_lines=args.skip_head_lines,
                      skip_tail_lines=args.skip_tail_lines))
        data = np.array([c for s in data for c in s], dtype=np.int32)
        if args.save_data:
            np.save(args.data_path + '.npy', data)
            u.save_model(d, args.dict_path + '.dict')
        data = torch.LongTensor(data.astype(np.int64))
    print("Splitting dataset...")
    train, valid, test = BlockDataset.splits_from_data(
        data, d, args.batch_size, args.bptt, gpu=args.gpu,
        test=args.test_split, dev=args.dev_split)
    del data

    print(' * vocabulary size. %d' % len(d))
    print(' * number of train examples. %d' % len(train.data))

    model.set_dropout(args.dropout)

    if args.gpu:
        model.cuda()

    print(model)
    print('* number of parameters: %d' % model.n_params())

    optim = Optimizer(
        model.parameters(), args.optim, args.learning_rate, args.max_grad_norm,
        lr_decay=args.learning_rate_decay, start_decay_at=args.start_decay_at,
        decay_every=args.decay_every)
    criterion = nn.NLLLoss()

    # create trainer
    trainer = LMTrainer(model, {"train": train, "test": test, "valid": valid},
                        criterion, optim)

    # check hooks:
    early_stopping = None
    if args.early_stopping > 0:
        early_stopping = EarlyStopping(args.early_stopping)

    model_check_hook = make_lm_check_hook(
        d, method=args.decoding_method, temperature=args.temperature,
        max_seq_len=args.max_seq_len, seed_text=args.seed, gpu=args.gpu,
        early_stopping=early_stopping)
    trainer.add_hook(model_check_hook, hooks_per_epoch=args.hooks_per_epoch)

    # save hooks:
    model_save_hook = make_lm_save_hook(d, args)
    trainer.add_hook(model_save_hook, hooks_per_epoch=args.saves_per_epoch)

    # loggers
    visdom_logger = VisdomLogger(
        log_checkpoints=args.log_checkpoints, title=args.prefix,
        env='weasimov', server='http://146.175.11.197')

    trainer.add_loggers(StdLogger(), visdom_logger)
    if args.csv:
        trainer.add_loggers(CSVLogger(args=args, save_path=args.csv))

    trainer.train(args.epochs, args.checkpoint, gpu=args.gpu)

    if args.save:
        test_ppl = trainer.validate_model(test=True)
        print("Test perplexity: %g" % test_ppl)
        if args.save:
            save_model(d, trainer.model, args, test_ppl)
