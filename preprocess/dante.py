import os
import random
import time
import requests
import lxml.etree
import pandas as pd


def query(isbn, api_key, url='http://db.meta4books.be/REST/onix3plus/product/isbn'):
    try:
        request = requests.get(url, params={'key': api_key, 'isbn': isbn})
        tree = lxml.etree.fromstring(request.content)
        return lxml.etree.tostring(tree, pretty_print=True, encoding='utf-8').decode()
    except:
        return None


def get_nonexistant_path(fname):
    if not os.path.exists(fname):
        return fname
    filename, file_extension = os.path.splitext(fname)
    i = 1
    new_fname = "{}-{}{}".format(filename, i, file_extension)
    while os.path.exists(new_fname):
        i += 1
        new_fname = "{}-{}{}".format(filename, i, file_extension)
    return new_fname


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_list', type=str)
    parser.add_argument('--output_dir', type=str)
    args = parser.parse_args()
    key = '71c7a8ea046120c1072509033ad5e515e20063d394ac67c4677cacee7129493c'
    df = pd.read_csv(args.file_list).fillna('')
    i = 0
    for _, row in df.iterrows():
        isbns_list = row.isbn.split(';')
        if not isbns_list[0]:
            continue
        print(i, row.filepath)
        for isbns in isbns_list:
            isbns = isbns.split(',')
            if len(isbns) == 3:
                _, _, isbn = isbns
                if isbn:
                    t = query(isbn, key)
                    if t is not None:
                        fp = get_nonexistant_path(os.path.join(args.output_dir, row.filepath + ".xml"))
                        with open(fp, "w") as outfile:
                            outfile.write(t)
                    time.sleep(random.randint(2, 8))
                    i += 1
