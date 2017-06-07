# -*- coding: utf-8 -*-

import random
import glob

random.seed(12101985)

def load_data(path='data/bigmama/',
              include_paragraphs=True,
              paragraph='<par>',
              level='token',
              max_files=None):
    
    filenames = glob.glob(path+'/*.txt')
    filenames.shuffle()
    if max_files:
        filenames = filenames[:max_files]

    for fn in filenames:
        for line in open(fn, 'r'):
            if not l.strip():
                if include_paragraphs:
                    yield [paragraph]
            else:
                if level == 'token':
                    yield l.strip().split()
                elif level == 'char':
                    yield list(l.strip())
