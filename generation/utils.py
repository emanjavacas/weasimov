# -*- coding: utf-8 -*-

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
              level='token',
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
            me = meta.loc(os.path.basename(fn))
            if filters['authors'] and me['author'] not in filters['authors']:
                continue
            if filters['titles'] and me['title'] not in filters['titles']:
                continue
            filenames.append(fn)
    else:
        filenames = glob.glob(path+'/*.txt')

    random.shuffle(filenames)

    if max_files:
        filenames = filenames[:max_files]

    for fn in filenames:
        for l in open(fn, 'r'):
            if not l.strip():
                if include_paragraphs:
                    yield [paragraph]
            else:
                if level == 'token':
                    yield l.strip().split()
                elif level == 'char':
                    yield list(l.strip())
