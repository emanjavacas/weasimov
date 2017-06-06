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
    for f in glob.glob("../data/tokenized/*.txt"):
        print(f)
        fname = os.path.basename(f)
        with open(f'../data/tokenized-quote-correction/{fname}', 'w') as outfile:
            for line in correct(f):
                outfile.write(f'{line}\n')
