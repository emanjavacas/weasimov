
import os
import sys

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

from seqmod.misc.trainer import LMTrainer
from seqmod.misc.loggers import StdLogger, VisdomLogger
from seqmod.misc.optimizer import Optimizer
from seqmod.misc.dataset import Dict, BlockDataset
from seqmod.misc.early_stopping import EarlyStopping

from utils import load_data


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


# hook
def make_lm_check_hook(d, seed_text, max_seq_len=25, gpu=False,
                       method='sample', temperature=1., width=5,
                       early_stopping=None, validate=True):

    seed_texts = None if not seed_text else [seed_text]
    def hook(trainer, epoch, batch_num, checkpoint):
        trainer.log("info", "Checking training...")
        if validate:
            loss = trainer.validate_model()
            trainer.log("info", "Valid loss: %g" % loss)
            trainer.log("info", "Registering early stopping loss...")
            if early_stopping is not None:
                early_stopping.add_checkpoint(loss)
        trainer.log("info", "Generating text...")
        scores, hyps = trainer.model.generate(
            d, seed_texts=seed_texts, max_seq_len=max_seq_len, gpu=gpu,
            method=method, temperature=temperature, width=width)
        hyps = [u.format_hyp(score, hyp, hyp_num + 1, d)
                for hyp_num, (score, hyp) in enumerate(zip(scores, hyps))]
        trainer.log("info", '\n***' + ''.join(hyps) + "\n***")

    return hook


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
    # dataset
    parser.add_argument('--path')
    parser.add_argument('--corpus', type=str, default='data/asimov')
    parser.add_argument('--load_data', action='store_true')
    parser.add_argument('--save_data', action='store_true')
    parser.add_argument('--dict_path', type=str)
    parser.add_argument('--data_path', type=str)
    parser.add_argument('--max_size', default=25000, type=int)
    parser.add_argument('--min_freq', default=1, type=int)
    parser.add_argument('--level', default='char')
    parser.add_argument('--filter_titles')
    parser.add_argument('--filter_authors')
    parser.add_argument('--sep', default=',')
    parser.add_argument('--dev_split', default=0.0001, type=float)
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
    parser.add_argument('--temperature', default=1, type=float)
    parser.add_argument('--checkpoint', default=100, type=int)
    parser.add_argument('--hooks_per_epoch', default=200, type=int)
    parser.add_argument('--log_checkpoints', action='store_true')
    parser.add_argument('--visdom_server', default='localhost')
    parser.add_argument('--save', action='store_true')
    parser.add_argument('--prefix', default='model', type=str)
    args = parser.parse_args()

    if args.load_data:
        print("Loading preprocessed datasets...")
        assert args.dict_path, "Processed data requires DICT_PATH"
        data, d = load_from_file(args.data_path), u.load_model(args.dict_path)
    else:
        print("Loading data...")
        d = Dict(max_size=args.max_size, min_freq=args.min_freq,
                 eos_token=u.EOS, bos_token=u.BOS)
        filters = {}
        if args.filter_titles:
            filters['titles'] = args.filter_titles.split(args.sep)
        if args.filter_authors:
            filters['authors'] = args.filter_authors.split(args.sep)
        d.fit(load_data(path=args.corpus, level=args.level, filters=filters))
        data = d.transform(load_data(level=args.level, filters=filters))
        data = np.array([c for s in data for c in s], dtype=np.int32)
        if args.save_data:
            np.save(args.data_path + '.npy', data)
            u.save_model(d, args.dict_path + '.dict')
        data = torch.LongTensor(data.astype(np.int64))
    train, valid, test = BlockDataset.splits_from_data(
        data, d, args.batch_size, args.bptt, gpu=args.gpu,
        test=args.test_split, dev=args.dev_split)
    del data

    print(' * vocabulary size. %d' % len(d))
    print(' * number of train examples. %d' % len(train.data))

    print('Building model...')
    model = LM(len(d), args.emb_dim, args.hid_dim,
               num_layers=args.layers, cell=args.cell, dropout=args.dropout,
               att_dim=args.att_dim, tie_weights=args.tie_weights,
               deepout_layers=args.deepout_layers,
               deepout_act=args.deepout_act, word_dropout=args.word_dropout,
               target_code=d.get_unk())

    model.apply(u.make_initializer())
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

    # hooks
    early_stopping = None
    if args.early_stopping > 0:
        early_stopping = EarlyStopping(args.early_stopping)
    model_check_hook = make_lm_check_hook(
        d, method=args.decoding_method, temperature=args.temperature,
        max_seq_len=args.max_seq_len, seed_text=args.seed, gpu=args.gpu,
        early_stopping=early_stopping)
    num_checkpoints = len(train) // (args.checkpoint * args.hooks_per_epoch)
    trainer.add_hook(model_check_hook, num_checkpoints=num_checkpoints)

    # loggers
    visdom_logger = VisdomLogger(
        log_checkpoints=args.log_checkpoints, title=args.prefix, env='lm',
        server='http://' + args.visdom_server)
    trainer.add_loggers(StdLogger(), visdom_logger)

    trainer.train(args.epochs, args.checkpoint, gpu=args.gpu)

    if args.save:
        test_ppl = trainer.validate_model(test=True)
        print("Test perplexity: %g" % test_ppl)
        if args.save:
            f = '{prefix}.{cell}.{layers}l.{hid_dim}h.{emb_dim}e.{bptt}b.{ppl}'
            fname = f.format(ppl="%.2f" % test_ppl, **vars(args))
            if os.path.isfile(fname):
                answer = input("File [%s] exists. Overwrite? (y/n): " % fname)
                if answer.lower() not in ("y", "yes"):
                    print("Goodbye!")
                    sys.exit(0)
            print("Saving model to [%s]..." % fname)
            u.save_model({'model': model.cpu(), 'dict': d}, fname)
