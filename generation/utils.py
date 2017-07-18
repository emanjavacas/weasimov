# -*- coding: utf-8 -*-

import os
import random
import glob

import pandas as pd

import seqmod.utils as u

random.seed(1001)


def _parse_filter_file(fn):
    df = pd.read_csv(fn, header=0, sep=';', dtype=str)
    df = df.set_index('filters').fillna('')
    filters = {}
    for f in ('authors', 'titles', 'genres'):
        try:
            vals = df.loc[f]['values'].split(',')
            filters[f] = set([v.strip() for v in vals])
        except:
            pass
    return filters


def parse_filter_file(fn, sep=';'):
    filters = {}
    with open(fn, 'r') as f:
        next(f)                 # skip header
        for line in f:
            filt, *values = line.split(sep)
            if filt not in ('authors', 'titles', 'genres'):
                continue
            filters[filt] = set([v.strip() for v in values])
    return filters


def filter_filenames(meta, path, filters):
    filenames = []
    for fn in glob.glob(path+'/*.txt'):
        me = meta.loc[os.path.splitext(os.path.basename(fn))[0]]
        if me.empty:
            continue
        if 'authors' in filters and \
           me['author:id'] not in filters['authors']:
            continue
        if 'titles' in filters and \
           str(me['title:detail']).strip() not in filters['titles']:
            continue
        if 'genres' in filters:
            match = False
            for f in filters['genres']:
                if f in me['categories'].lower():
                    match = True
                    continue
            if not match:
                continue
        filenames.append(fn)

    return filenames


def load_data(path='data/bigmama/',
              metapath='/home/mike/GitRepos/weasimov/metainfo.csv',
              filter_file=None,
              include_paragraphs=False,
              paragraph='<par>',
              level='char',
              max_files=None,
              filters={},
              skip_head_lines=0,
              skip_tail_lines=0):
    """
    Yields data for training a language model.

    Iterator that yields sentences, tokens or characters for training.

    E.g.
    filters={'authors':['31666', '34508', '38668'],
             'titles':['Coraline', 'Kardinaal van het Kremlin'],
             'genres':['thriller', 'romantiek']}

    Notes
    -----
    * Text will be included if ALL the filters yield a match for the file.
    * Note that genres are partially matched.
    * The `filters` option will be overridden if you specify a `filter_file`.

    """

    meta = load_metadata(fn=metapath)

    if filter_file:
        filters = parse_filter_file(filter_file)

    if filters:
        filenames = filter_filenames(meta, path, filters)
    else:
        filenames = glob.glob(path + '/*.txt')

    random.shuffle(filenames)

    if max_files:
        filenames = filenames[:max_files]

    for idx, fn in enumerate(filenames):
        if idx % 200 == 0:
            print(idx, fn)
        if skip_head_lines or skip_tail_lines:
            with open(fn, 'r') as inf:
                lines = inf.readlines()
                if len(lines) > 100:
                    lines = lines[skip_head_lines:-skip_tail_lines]
                for l in lines:
                    l = l.strip()
                    if l:
                        if level == 'token':
                            yield l.strip().split()
                        elif level == 'char':
                            yield list(l.strip())
        else:
            for l in open(fn, 'r'):
                if not l.strip():
                    if include_paragraphs:
                        yield [paragraph]
                else:
                    if level == 'token':
                        yield l.strip().split()
                    elif level == 'char':
                        yield list(l.strip())


def format_hyp(score, hyp, hyp_num, d):
    """
    Transform a hypothesis into a string for visualization purposes

    score: float, normalized probability
    hyp: list of integers
    hyp_num: int, index of the hypothesis
    d: Dict, dictionary used for fitting the vocabulary
    """
    return '\n* [{hyp}] [Score:{score:.3f}]: {sent}'.format(
        hyp=hyp_num, score=score/len(hyp),
        sent=' '.join([d.vocab[c] for c in hyp]))


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
