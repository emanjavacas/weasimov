import glob
import os
import shutil
import random
from collections import Counter


def main(indir, outdir, max_nb_files, min_char_freq):
    indir = os.path.expanduser(indir)
    outdir = os.path.expanduser(outdir)
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.mkdir(outdir)

    filenames = glob.glob(indir + '/*.txt')
    if max_nb_files:
        random.shuffle(filenames)
        filenames = filenames[:max_nb_files]
    char_cnt = Counter()

    print('-> Establishing char frequencies...')
    for filename in filenames:
        print('  -', filename)
        for line in open(filename, 'r'):
            char_cnt.update(line)

    print('Original character distribution:', str(char_cnt))
    vocab = set([char for char, cnt in char_cnt.items()
                 if cnt >= min_char_freq])
    print('Pruned character vocabulary:', sorted(vocab))

    print('-> Pruning files...')
    for filename in filenames:
        print('  -', filename)
        bn = os.path.basename(filename)
        with open(os.sep.join((outdir, bn)), 'w') as outf:
            for line in open(filename):
                line = ''.join([c for c in line if c in vocab])
                if line.strip():
                    outf.write(line.lstrip())


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--indir', type=str)
    parser.add_argument('--outdir', type=str, default='cleaned')
    parser.add_argument('--max_nb_files', default=None, type=int)
    parser.add_argument('--min_char_freq', default=5000, type=int)
    args = parser.parse_args()

    main(indir=args.indir,
         outdir=args.outdir,
         max_nb_files=args.max_nb_files,
         min_char_freq=args.min_char_freq)
