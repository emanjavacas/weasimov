
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

from utils import load_data, format_hyp


def load_from_file(path):
    if path.endswith('npy'):
        import numpy as np
        array = np.load(path).astype(np.int64)
        data = torch.LongTensor(array)
    elif path.endswith('.pt'):
        data = torch.load(path)
    else:
        raise ValueError('Unknown input format [%s]' % path)
    return data


# check hook
def make_lm_check_hook(d, seed_text, max_seq_len=25, gpu=False,
                       method='sample', temperature=.5, width=5,
                       early_stopping=None, validate=True,
                       nb_temperatures=3):

    dpath = os.path.dirname(os.path.realpath(__file__))
    fpath = os.sep.join((dpath, 'seed-sentences.txt'))
    seed_texts = [l.strip() for l in open(fpath, 'r')]
    temperatures = np.linspace(0.1, temperature, nb_temperatures)
    s = re.compile(r' +')
    ss = re.compile(r"(?<=\S)\s(?=\S)")

    def hook(trainer, epoch, batch_num, checkpoint):
        trainer.log("info", "Checking training...")
        if validate:
            loss = trainer.validate_model()
            trainer.log("info", "Valid loss: %g" % loss)
            trainer.log("info", "Registering early stopping loss...")
            if early_stopping is not None:
                early_stopping.add_checkpoint(loss)
        trainer.log("info", "Generating text...")
        for temp in temperatures:
            trainer.log("info", "Temperature at " + "%.2f" % temp)
            scores, hyps = trainer.model.generate(
                d, seed_texts=seed_texts, max_seq_len=max_seq_len, gpu=gpu,
                method=method, temperature=temp, width=width)
            hyps = [format_hyp(score, hyp, s.sub('  ', st)[:25]+'...', d)
                    for hyp_num, (score, st, hyp)
                    in enumerate(zip(scores, seed_texts, hyps))]
            hyps = [ss.sub('', h) for h in hyps]
            hyps = [s.sub(' ', h) for h in hyps]
            trainer.log("info", '\n***' + ''.join(hyps) + "\n***")

    return hook


# check hook
def make_lm_save_hook(d, args):

    def hook(trainer, epoch, batch_num, checkpoint):
        trainer.log("info", "Saving model...")
        save_model(d, trainer.model, args, ppl=None)
        if args.gpu:
            trainer.model.cuda()

    return hook


def save_model(d, model, args, ppl=None):
    fname = '{prefix}.{cell}.{layers}l.{hid_dim}h.{emb_dim}e.{bptt}b'

    if ppl:  # add test ppl to final save
        fname += '.{ppl}'
        fname = fname.format(ppl="%.2f" % ppl, **vars(args))
    else:
        fname = fname.format(**vars(args))

    u.save_model({'model': model.cpu(),
                  'dict': d,
                  'train_params': vars(args)},
                 fname)
    print("Model saved to [%s]..." % fname)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    # model
    parser.add_argument('--layers', default=1, type=int)
    parser.add_argument('--cell', default='LSTM')
    parser.add_argument('--emb_dim', default=50, type=int)
    parser.add_argument('--hid_dim', default=2064, type=int)
    parser.add_argument('--att_dim', default=0, type=int)
    parser.add_argument('--dropout', default=0.2, type=float)
    parser.add_argument('--word_dropout', default=0.0, type=float)
    parser.add_argument('--tie_weights', action='store_true')
    parser.add_argument('--deepout_layers', default=0, type=int)
    parser.add_argument('--deepout_act', default='MaxOut')
    parser.add_argument('--load_model', action='store_true')
    parser.add_argument('--model_path', help=('Path to pretrained model. ' +
                                              'Required if --load_model'))
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
    parser.add_argument('--max_size', default=100000, type=int,
                        help='Maximum items in the dictionary')
    parser.add_argument('--min_freq', default=1, type=int,
                        help=('Minimum frequency for an item to be ' +
                              'included in the dictionary'))
    parser.add_argument('--level', default='char')
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

    # logger
    parser.add_argument('--csv', type=str, default=' ')
    parser.add_argument('--note', type=str, default=" ", nargs='+')
    args = parser.parse_args()

    model, d, data = None, None, None

    # eventually load model and dict
    if args.load_model:
        assert args.model_path, "LOAD_MODEL needs MODEL_PATH"
        model = u.load_model(args.model_path)
        d, model = model['dict'], model['model']

    # prepare data
    if args.load_data:
        print("Loading preprocessed datasets...")
        assert args.dict_path, "Processed data requires DICT_PATH"
        data = load_from_file(args.data_path)
        d = d or u.load_model(args.dict_path)
    else:
        print("Loading data...")
        d = d or Dict(max_size=args.max_size, min_freq=args.min_freq,
                      eos_token=u.EOS, bos_token=u.BOS)
        if not d.fitted:
            print("Fitting dictionary...")
            d.fit(load_data(path=args.corpus, level=args.level,
                            filters=args.filter_file,
                            skip_head_lines=args.skip_head_lines,
                            skip_tail_lines=args.skip_tail_lines))
        print("Transforming data...")
        print(args.corpus)
        data = d.transform(
            load_data(path=args.corpus, level=args.level,
                      filters=args.filter_file,
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

    if model is None:
        print('Building model...')
        model = LM(len(d), args.emb_dim, args.hid_dim,
                   num_layers=args.layers, cell=args.cell,
                   dropout=args.dropout, att_dim=args.att_dim,
                   tie_weights=args.tie_weights,
                   deepout_layers=args.deepout_layers,
                   deepout_act=args.deepout_act,
                   word_dropout=args.word_dropout,
                   target_code=d.get_unk())
        model.apply(u.make_initializer())
    else:
        model.set_dropout(args.dropout)

    if args.gpu:
        model.cuda()

    print(model)
    print('* number of parameters: %d' % model.n_params())

    optim = Optimizer(
        model.parameters(), args.optim, args.learning_rate, args.max_grad_norm,
        lr_decay=args.learning_rate_decay, start_decay_at=args.start_decay_at,
        decay_every=args.decay_every)
    criterion = nn.CrossEntropyLoss()

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
    num_checkpoints = max(1, len(train) // (args.checkpoint *
                                            args.hooks_per_epoch))
    trainer.add_hook(model_check_hook, num_checkpoints=num_checkpoints)

    # save hooks:
    model_save_hook = make_lm_save_hook(d, args)
    num_checkpoints = max(1, len(train) // (args.checkpoint *
                                            args.saves_per_epoch))
    trainer.add_hook(model_save_hook, num_checkpoints=num_checkpoints)

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
