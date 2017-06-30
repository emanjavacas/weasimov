
import os
import sys; sys.path.append(os.path.abspath("../generation"))
from utils import load_metadata, filter_filenames
import linecache
import glob
import subprocess
import random

random.seed(1001)


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
