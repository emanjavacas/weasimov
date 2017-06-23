import glob
import os
import shutil
import random
from collections import Counter

HYPHENS = '-–‐—−‑‒', '-'
QUOTES = "'′’”\"‚“„ʼ`ʻ‟«¨'´»‘˝″", "'"
SPACES = "\x94\x92\x9a\x96\u200b\x9c\x8e\x9d\x9e\x88", " "
STARS = "∗✷★", "*"
LIGATURES = 'ﬁ', 'fi'
GARBAGE = '�•·€¬©™', ''
MAPPINGS = HYPHENS, QUOTES, SPACES, STARS, LIGATURES, GARBAGE
CHAR_MAPPINGS = {c: r for chars, r in MAPPINGS for c in chars}
KEEP = 'Ë+ùÍìÓÜãÇ⁄ÈÁ'

def main(input_dir, output_dir, max_nb_files, min_char_freq):
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    filenames = os.scandir(input_dir)
    if max_nb_files:
        random.shuffle(filenames)
        filenames = filenames[:max_nb_files]
    char_cnt = Counter()

    print('-> Establishing char frequencies...')
    for i, filename in enumerate(filenames):
        print(f'{i: <8}-{filename.name}')
        with open(filename.path) as infile:
            char_cnt.update(infile.read())

    print('Original character vocabulary:', ''.join(sorted(char_cnt)))

    replacer = str.maketrans(CHAR_MAPPINGS)
    deletable = ''.join(char for char, cnt in char_cnt.items()
                        if cnt < min_char_freq and char not in KEEP)
    deleter = str.maketrans('', '', deletable)

    print('Pruned character vocabulary:', ''.join(sorted(set(''.join(char_cnt).translate(replacer).translate(deleter)))))

    print('-> Pruning files...')
    for i, filename in enumerate(os.scandir(input_dir)):
        print(f'{i: <8}-{filename.name}')
        with open(filename.path) as infile:
            text = infile.read()
        text = text.translate(replacer).translate(deleter)
        with open(os.sep.join((output_dir, filename.name)), 'w') as outfile:
            outfile.write(text)


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str)
    parser.add_argument('--output_dir', type=str, default='cleaned')
    parser.add_argument('--max_nb_files', default=None, type=int)
    parser.add_argument('--min_char_freq', default=2000, type=int)
    args = parser.parse_args()

    main(args.input_dir, args.output_dir, args.max_nb_files, args.min_char_freq)
