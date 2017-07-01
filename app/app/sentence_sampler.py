
import os
import linecache
import glob
import subprocess
import random

import pandas as pd

random.seed(1001)


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


def load_metadata(fn):
    df = pd.read_csv(fn, header=0, sep=',', dtype={'author:id': str})
    df = df.set_index('filepath').fillna('')
    return df


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
