
import os
import sys
import re
import glob

import random; random.seed(1001)

import numpy as np

import torch; torch.manual_seed(1001)
try:
    torch.cuda.manual_seed(1001)
except:
    print('no NVIDIA driver found')

import torch.nn as nn

from seqmod.modules.lm import LM
from seqmod import utils as u

from seqmod.misc.trainer import CLMTrainer
from seqmod.misc.loggers import StdLogger, VisdomLogger
from seqmod.misc.optimizer import Optimizer
from seqmod.misc.dataset import BlockDataset
from seqmod.misc.early_stopping import EarlyStopping

from utils import make_lm_save_hook, save_model


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    # model
    parser.add_argument('--layers', default=1, type=int)
    parser.add_argument('--cell', default='LSTM')
    parser.add_argument('--emb_dim', default=50, type=int)
    parser.add_argument('--hid_dim', default=2064, type=int)
    parser.add_argument('--cond_emb_dim', default=24, type=int)
    parser.add_argument('--dropout', default=0.2, type=float)
    parser.add_argument('--word_dropout', default=0.0, type=float)
    parser.add_argument('--tie_weights', action='store_true')
    parser.add_argument('--deepout_layers', default=0, type=int)
    parser.add_argument('--deepout_act', default='MaxOut')
    parser.add_argument('--load_model', action='store_true')
    parser.add_argument('--model_path', help=('Path to pretrained model. ' +
                                              'Required if --load_model'))
    # dataset
    parser.add_argument('--data_dir', help='Path to dir with preprocessed data',
                        required=True)
    parser.add_argument('--dev_split', default=0.01, type=float)
    parser.add_argument('--test_split', default=0.05, type=float)
    # training
    parser.add_argument('--epochs', default=10, type=int)
    parser.add_argument('--batch_size', default=264, type=int)
    parser.add_argument('--bptt', default=200, type=int)
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
    parser.add_argument('--prefix', default='model', type=str)
    args = parser.parse_args()

    print("Loading training data...")
    d = u.load_model(os.path.join(args.data_dir, "dataset.dict.pt"))
    lang_d, *conds_d = d

    # conditional structure
    conds = []
    print(' * vocabulary size. %d' % len(lang_d))
    for idx, subd in enumerate(conds_d):
        print(' * condition [%d] with cardinality %d' % (idx, len(subd)))
        conds.append({'varnum': len(subd), 'emb_dim': args.cond_emb_dim})

    if args.load_model:
        print('Loading model...')
        assert args.model_path, "load_model requires model_path"
        model = u.load_model(args.model_path)
    else:
        print('Building model...')
        model = LM(len(lang_d), args.emb_dim, args.hid_dim,
                   num_layers=args.layers, cell=args.cell,
                   dropout=args.dropout, tie_weights=args.tie_weights,
                   deepout_layers=args.deepout_layers,
                   deepout_act=args.deepout_act,
                   word_dropout=args.word_dropout,
                   target_code=lang_d.get_unk(), conds=conds)
        model.apply(u.make_initializer())

    print(model)
    print(' * n parameters. %d' % model.n_params())

    if args.gpu:
        model.cuda()

    optim = Optimizer(
        model.parameters(), args.optim, args.learning_rate, args.max_grad_norm,
        lr_decay=args.learning_rate_decay, start_decay_at=args.start_decay_at,
        decay_every=args.decay_every)
    criterion = nn.NLLLoss()

    # hooks
    early_stopping = None
    if args.early_stopping > 0:
        early_stopping = EarlyStopping(args.early_stopping)
    check_hook = u.make_clm_hook(
        d, max_seq_len=args.max_seq_len, samples=5, gpu=args.gpu,
        method=args.decoding_method, temperature=args.temperature)
    # save hooks
    model_save_hook = make_lm_save_hook(d, args)

    # loggers
    visdom_logger = VisdomLogger(
        log_checkpoints=args.log_checkpoints, title=args.prefix,
        env='weasimov', server='http://146.175.11.197')
    std_logger = StdLogger()

    # batched trainer
    for epoch in range(args.epochs):
        for f in glob.glob(args.data_dir + '/dataset_[0-9].pt'):
            print("loading data from [%s]" % f)
            examples = tuple(u.load_model(f).contiguous())
            # dataset
            train, valid, test = BlockDataset.splits_from_data(
                examples, d, args.batch_size, args.bptt, gpu=args.gpu,
                test=args.test_split, dev=args.dev_split)
            # trainer
            trainer = CLMTrainer(
                model, {'train': train, 'valid': valid, 'test': test},
                criterion, optim)
            trainer.log("info", "Full dataset epoch [%d]" % epoch)
            trainer.add_loggers(std_logger, visdom_logger)
            trainer.add_hook(check_hook, hooks_per_epoch=args.hooks_per_epoch)
            trainer.add_hook(
                model_save_hook, hooks_per_epoch=args.saves_per_epoch)
            trainer.train(1, args.checkpoint, gpu=args.gpu)

    if args.save:
        test_ppl = trainer.validate_model(test=True)
        print("Test perplexity: %g" % test_ppl)
        if args.save:
            save_model(d, trainer.model, args, test_ppl)
