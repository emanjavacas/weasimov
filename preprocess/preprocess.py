import argparse
import os
import re
import tarfile

import nltk

quotes = re.compile('|'.join(tuple("«‹»›„‚“‟‘‛”’\"❛❜❝❞❮❯⹂〝〞〟＂\'`")))

def tokenize_document(fname, text, output_dir):
    sentences = nltk.sent_tokenize(text)
    tokenized = re.sub(quotes, "'", '\n'.join(sentences))
    outfile = os.path.join(output_dir, fname)
    if os.path.exists(outfile):
        outfile += '-2.txt'
    with open(outfile, 'w') as outfile:
        outfile.write(tokenized)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str)
    args = parser.parse_args()

    if args.input_dir.endswith('.tar.gz'):
        tar = tarfile.open(args.input_dir)
        for fname in tar.getmembers():
            print(fname)
            text = tar.extractfile(fname).read()
            tokenize_document(fname, text, args.output_dir)
    else:
        for fname in os.scandir(args.input_dir):
            with open(fname.path) as infile:
                text = infile.read()
            print(fname.name)
            tokenize_document(fname.name, text, args.output_dir)
