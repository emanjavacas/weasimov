import os
import ucto

tokenizer = ucto.Tokenizer("tokconfig-nld", quotedetection=True)

def split_sentences(string):
    tokenizer.process(string)
    sentence = ''
    for token in tokenizer:
        sentence += str(token)
        if token.isendofsentence():
            yield sentence
            sentence = ''
        elif not token.nospace():
            sentence += " "
    if sentence:
        yield sentence

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str)
    parser.add_argument("--extension", type=str, default=".txt")
    args = parser.parse_args()

    for fname in os.listdir(args.input_dir):
        if fname.endswith(args.extension):
            with open(os.path.join(args.input_dir, fname)) as infile:
                text = infile.read()
            with open(os.path.join(args.output_dir, fname), 'w') as outfile:
                for sentence in split_sentences(text):
                    outfile.write(sentence + "\n")
