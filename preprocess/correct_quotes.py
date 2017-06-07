import glob
import os

# after tokenization, correct sequences of quotes into dialog paragraphs

quotes = tuple("«‹»›„‚“‟‘‛”’\"❛❜❝❞❮❯⹂〝〞〟＂\'")

def correct(f):
    par_break, prev_quote = False, False
    quote = []
    for line in open(f):
        line = line.strip()
        if line.startswith(quotes) and (par_break or quote):
            par_break = False
            quote.append(line)
        elif not line:
            par_break = True
            if not quote:
                yield ''
        else:
            par_break = False
            if quote:
                yield '\n'.join(quote) + '\n'
            yield line
            quote = []

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('output_path')
    args = parser.parse_args()

    for f in glob.glob("{path}/*.txt".format(**vars(args))):
        print(f)
        fname = os.path.basename(f)
        with open(os.path.join(args.output_path, fname), 'w') as outfile:
            for line in correct(f):
                outfile.write(line + '\n')
