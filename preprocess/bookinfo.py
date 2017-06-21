
import os
import re
import logging
import html.parser
import zipfile
import isbnlib
import pandas as pd

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SPECIAL_ISBN = ['0000000000']
ISBN = re.compile(r'[- 0-9X]{10,19}', re.M | re.S)


class EbookReader(html.parser.HTMLParser):
    def __init__(self, fname):
        super().__init__()
        self.fname = fname
        self.content = ''

    def handle_data(self, data):
        self.content += data

    def parse(self):
        try:
            zf = zipfile.ZipFile(self.fname, 'r')
            html_files = [f for f in zf.filelist if f.filename.endswith("html")]
            for html_file in html_files:
                try:
                    self.feed(str(zf.read(html_file)))
                except KeyError:
                    logger.debug(f"File not found in Zipfile {self.fname}")
        except (zipfile.BadZipFile, zipfile.zlib.error):
            logger.debug(f'Exception in ZipFile {self.fname}.')
            pass


def extract_isbn(ebook):
    isbns = set()
    for match in ISBN.finditer(ebook.content):
        isbn = match.group()
        isbn = ''.join(c.upper() if c in 'isbn' else c for c in isbn)
        isbn = re.sub(r'ISBN', 'ISBN\x20', re.sub(r'\x20', '', isbn))
        if isbn not in SPECIAL_ISBN:
            try:
                canonical_isbn = isbnlib.get_canonical_isbn(isbn)
            except IndexError:
                continue
            isbn_formats = []
            if canonical_isbn:
                isbn_formats.append(canonical_isbn)
                isbn_formats.append(isbnlib.to_isbn10(canonical_isbn) or '')
                isbn_formats.append(isbnlib.to_isbn13(canonical_isbn) or '')
            isbns.add(','.join(isbn_formats))
    return isbns


def common_name(fname):
    name, _ = os.path.splitext(fname)
    return name


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dirs", nargs='+')
    parser.add_argument("--output_file", type=str)
    args = parser.parse_args()
    data = {}
    i = 0
    for directory in args.input_dirs:
        for fname in os.scandir(directory):
            if i % 100 == 0:
                print(f"Processed {i} books.")
            if fname.name.endswith(".epub"):
                cname = common_name(fname.name)
                if cname in data and data[cname]:
                    continue
                ebook = EbookReader(fname.path)
                ebook.parse()
                isbns = extract_isbn(ebook)
                data[cname] = ';'.join(l for l in isbns if l)
            i += 1
    df = pd.DataFrame(list(data.items()), columns=['filepath', 'isbn'])
    df.to_csv(args.output_file, index=False, encoding='utf-8')
