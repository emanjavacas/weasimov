# -*- coding: utf-8 -*-

import os
import random
import subprocess
import glob
import linecache
import random

import pandas as pd

random.seed(12101985)


def load_metadata(fn):
    df = pd.read_csv(fn, header=0, sep=',', dtype={'author:id': str})
    df = df.set_index('filepath').fillna('')
    return df


def parse_filter_file(fn):
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
    return '\n* [{hyp}] [Score:{score:.3f}]: {sent}'.format(
        hyp=hyp_num, score=score/len(hyp),
        sent=' '.join([d.vocab[c] for c in hyp]))


def file_len(fname):
    """
    Unix-only, but much fast than reading the entire file.
    """
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])


def random_sentence(filedir='/home/karsdorp/weasimov/data/' +
                            'weasimov-novels-tokenized-cleaned',
                    metapath='metainfo.csv',
                    min_len=25,
                    filters=None):
    random.seed()

    if filters:
        meta = load_metadata(fn=metapath)
        filter_filenames(meta, filedir, filters)
    else:
        filenames = glob.glob(filedir + '/*.txt')

    rnd_sent = None
    while not rnd_sent:
        fname = random.choice(filenames)
        max_idx = file_len(fname)
        rnd_idx = random.randint(0, max_idx)
        pick = linecache.getline(fname, rnd_idx).strip()
        if pick and len(pick) >= min_len:
            rnd_sent = pick
    return rnd_sent
