import os
import ucto
import lxml.etree
import pdb

BEGINQUOTE, ENDQUOTE = ucto.TokenRole.BEGINQUOTE, ucto.TokenRole.ENDQUOTE

def split_sentences(text, tokenizer):
    tokenizer.process(text)
    sentence, i, open_quote, new_par = '', 0, 0, False
    prev_ending = False
    for token in tokenizer:
        i += 1
        if token.isnewparagraph():
            new_par = True
        if prev_ending and token.isbeginofsentence() and not open_quote:
            yield sentence, new_par
            sentence, i, new_par = '', 0, False
        prev_ending = True if token.isendofsentence() else False
        if token.role == BEGINQUOTE:
            open_quote += 1
        elif token == ENDQUOTE:
            open_quote -= 1
        sentence += str(token)
        if not token.nospace():
            sentence += ' '
        if token.isendofsentence() and i > 200 and open_quote:
            print("Rollback quote runaway...")
            print(sentence)
            tok_backup = ucto.Tokenizer("tokconfig-nld")
            yield from split_sentences(sentence, tok_backup)
            sentence, i, open_quote, new_par = '', 0, 0, False
    if sentence:
        yield sentence, new_par

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str)
    parser.add_argument("--extension", type=str, default=".txt")
    args = parser.parse_args()

    tokenizer = ucto.Tokenizer("tokconfig-nld", quotedetection=True)

    for i, fname in enumerate(os.listdir(args.input_dir)):
        print(i, fname)
        if fname.endswith(args.extension):
            with open(os.path.join(args.input_dir, fname)) as infile:
                text = infile.read()
            with open(os.path.join(args.output_dir, fname), "w") as outfile:
                for sentence, new_par in split_sentences(text, tokenizer):
                    if new_par:
                        outfile.write('\n')
                    outfile.write(sentence + "\n")
