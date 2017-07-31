
import os
from itertools import islice

import torch

from seqmod.misc.dataset import Dict, CompressionTable
import seqmod.utils as u


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def read_meta(path):
    import csv
    metadata = {}
    with open(path) as f:
        rows = csv.reader(f)
        header = next(rows)
        for row in rows:
            row = dict(zip(header, row))
            metadata[row['filepath']] = row
            for c in row['categories'].split(','):
                c = c.lower()
                if 'non-fictie' in c:
                    row['fictie'] = False
                elif 'fictie' in c:
                    row['fictie'] = True
                else:
                    row['fictie'] = 'NA'
    return metadata


def compute_length(l, length_bins):
    length = len(l)
    output = None
    for length_bin in length_bins[::-1]:
        if length > length_bin:
            output = length_bin
            break
    else:
        output = -1
    return output


def load_data(rootfiles, metapath,
              input_format='txt',
              include_length=True,
              length_bins=[50, 100, 150, 300],
              include_author=True,
              authors=(),
              include_fields=True,
              categories=('fictie',)):
    metadata = read_meta(metapath)
    for idx, f in enumerate(rootfiles):
        if idx % 200 == 0:
            print("Processed [%d] files" % idx)
        filename = os.path.basename(f)
        if os.path.splitext(filename)[0] in metadata:
            row = metadata[os.path.splitext(filename)[0]]
            conds = []
            if include_author:
                author = row['author:lastname']
                if (not authors) or author in authors:
                    conds.append(author)
            if include_fields:
                for c in categories:
                    conds.append(row[c])
            with open(f, 'r') as lines:
                for l in lines:
                    l = l.strip()
                    if not l:
                        continue
                    lconds = [c for c in conds]
                    if include_length:
                        lconds.append(compute_length(l, length_bins))
                    yield l, lconds
        else:
            print("Couldn't find [%s]" % f)


def chars_conds(lines, lang_d, conds_d, table=None):
    for line, line_conds in lines:
        line_conds = tuple(d.index(c) for d, c in zip(conds_d, line_conds))
        for char in next(lang_d.transform([line])):
            yield char
            if table is None:
                for c in line_conds:
                    yield c
            else:
                yield table.hash_vals(line_conds)


def examples_from_lines(lines, lang_d, conds_d, table=None):
    gen = chars_conds(lines, lang_d, conds_d, table=table)
    dims = 2 if table is not None else len(conds_d) + 1
    return torch.LongTensor(list(gen)).view(-1, dims).t().contiguous()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_path', required=True)
    parser.add_argument('--metapath', default='metainfo.csv')
    parser.add_argument('--corpus', type=str, default='data/asimov',
                        help='Path to dir with input files')
    parser.add_argument('--max_size', default=100000, type=int,
                        help='Maximum items in the dictionary')
    parser.add_argument('--min_freq', default=1, type=int,
                        help=('Minimum frequency for an item to be ' +
                              'included in the dictionary'))
    parser.add_argument('--filesbatch', default=500, type=int)
    parser.add_argument('--level', default='char')
    args = parser.parse_args()

    filenames = [os.path.join(args.corpus, f)
                 for f in os.listdir(args.corpus)]

    # dictionaries
    dict_path = os.path.join(args.save_path, 'dataset.dict')
    if os.path.exists(dict_path + '.pt'):
        print("Loading dicts")
        d = u.load_model(dict_path + '.pt')
        lang_d, *conds_d = d
    else:
        print("Fitting dictionaries")
        lang_d = Dict(
            max_size=args.max_size, min_freq=args.min_freq, eos_token=u.EOS)
        lines = load_data(filenames, args.metapath)
        nconds = len(next(lines)[1])
        conds_d = [Dict(sequential=False, force_unk=False)
                   for _ in range(nconds)]
        ls, cs = zip(*lines)
        print("Fitting language Dict")
        lang_d.fit(ls)
        print("Fitting condition Dicts")
        for d, c in zip(conds_d, zip(*cs)):
            d.fit([c])
        print("Saving dicts")
        u.save_model([lang_d] + conds_d, dict_path)

    # dataset
    print("Transforming dataset")
    table = CompressionTable(len(conds_d))
    for batch_num, batch in enumerate(chunk(filenames, args.filesbatch)):
        batch_path = '{path}/dataset_{batch_num}'.format(
            path=args.save_path, batch_num=batch_num)
        lines = load_data(batch, args.metapath)
        tensor = examples_from_lines(lines, lang_d, conds_d, table=table)
        u.save_model(tensor, batch_path)
        del tensor
