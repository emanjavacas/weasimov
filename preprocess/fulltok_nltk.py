"""
Example usage:
python fulltok_nltk.py --input_dir="/home/mike/weasimov_data/04cleaned" --output_dir="/home/mike/weasimov_data/05token" --extension=".txt"
"""

import argparse
import os
import re
from nltk.tokenize import word_tokenize

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str)
    parser.add_argument("--extension", type=str, default=".txt")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    for idx, fname in enumerate(os.scandir(args.input_dir)):
        if idx % 100 == 0:
            print(idx, fname.name)
        if fname.name.endswith(args.extension):
            outfile_path = os.sep.join((args.output_dir, fname.name))
            with open(outfile_path, 'w') as outfile:
                for line in open(fname.path):
                    line = line.strip()
                    if line:
                        tokens = word_tokenize(line, language='dutch')
                        outfile.write(' '.join(tokens)+'\n')
