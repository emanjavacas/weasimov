# -*- coding: utf-8 -*-

import os
import random
import glob

import pandas as pd

random.seed(12101985)


def load_metadata(fn):
    df = pd.read_csv(fn, sep=';')
    df = df.set_index('fname')
    return df


def load_data(path='data/bigmama/',
              include_paragraphs=True,
              paragraph='<par>',
              level='char',
              max_files=None,
              filters={}):
    """Yields data for training a language model.

    Iterator that yields sentences, tokens or characters for training.

    E.g.
    filters={'authors':['Pieter Aspe', 'Baantjer'],
             'titles':['Onder valse vlag']}
    """

    meta = load_metadata(fn='meta.csv')

    if filters:
        filenames = []
        for fn in glob.glob(path+'/*.txt'):
            me = meta.loc[meta.index == os.path.basename(fn)]
            if me.empty:
                continue
            if 'authors' in filters and me['author'][0] not in filters['authors']:
                continue
            if 'titles' in filters and me['title'][0] not in filters['titles']:
                continue
            filenames.append(fn)
    else:
        filenames = glob.glob(path + '/*.txt')

    random.shuffle(filenames)

    if max_files:
        filenames = filenames[:max_files]

    for idx, fn in enumerate(filenames):
        if idx % 200 == 0:
            print(idx, fn)
        for l in open(fn, 'r'):
            if not l.strip():
                if include_paragraphs:
                    yield [paragraph]
            else:
                if level == 'token':
                    yield l.strip().split()
                elif level == 'char':
                    yield list(l.strip())