import os
import numpy as np


def coverage(text: str, stopwords: list) -> float:
    return sum(text.find(w) > -1 for w in stopwords) / len(stopwords)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--stopword_file", type=str, default='../data/stopwords.txt')
    args = parser.parse_args()

    with open(args.stopword_file) as infile:
        stopwords = [line.strip() for line in infile]

    coverages, fnames = [], []
    for fname in os.scandir(args.input_dir):
        with open(fname.path) as infile:
            coverages.append(coverage(infile.read(), stopwords))
            fnames.append(fname.path)
    coverages, fnames = np.array(coverages), np.array(fnames)
    sorting = coverages.argsort()
    coverages = coverages[sorting]
    fnames = fnames[sorting]

    print(coverages.mean())
    for fname, score in zip(fnames, coverages):
        print(fname, score)
