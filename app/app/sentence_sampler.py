
import os
import linecache
import glob
import subprocess
import random

import pandas as pd

random.seed(1001)


def _filter_filenames(meta, path, filters):
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


def filter_filenames(meta, path, filters):
    filenames = []
    for fn in glob.glob(path+'/*.txt'):
        filepath = os.path.splitext(os.path.basename(fn))[0]
        me = meta.get(filepath)
        if me is None:
            continue
        if 'authors' in filters and \
           me['author:id'] not in filters['authors']:
            continue
        if 'titles' in filters and \
           me['title:detail'] not in filters['titles']:
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


def _load_metadata(fn, sep=','):
    df = pd.read_csv(fn, header=0, sep=',', dtype={'author:id': str})
    df = df.set_index('filepath').fillna('')
    return df


def load_metadata(fn, sep=','):
    by_filepath = {}
    with open(fn, 'r') as f:
        header = next(f).strip().split(sep)
        for line in f:
            row = line.strip().split(sep)
            row_dict = {field: val for field, val in zip(header, row)}
            by_filepath[row_dict['filepath']] = row_dict
    return by_filepath


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


class RandomSentenceSampler(object):
    """
    Service providing random sampling of sentences from the training data

    Parameters
    ==========

    filedir: str, path to directory with corpus files
    metapath: str, path to file with metadata
    """
    def __init__(self, filedir, metapath):
        self.filedir = filedir
        self.metadata = load_metadata(fn=metapath)

    def sample(self, min_len=25, filters=None):
        if filters:
            filenames = filter_filenames(self.meta, self.filedir, filters)
        else:
            filenames = glob.glob(self.filedir + '/*.txt')

        rnd_sent = None
        while not rnd_sent:
            fname = random.choice(filenames)
            max_idx = file_len(fname)
            rnd_idx = random.randint(0, max_idx)
            pick = linecache.getline(fname, rnd_idx).strip()
            if pick and len(pick) >= min_len:
                rnd_sent = pick
        return rnd_sent
