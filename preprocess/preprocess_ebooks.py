import glob
import os
import zipfile

import bs4
import ebooklib
from ebooklib import epub
import lxml

# convert epubs into txt files. 

def main(input_path, output_path):
    for f in glob.glob('{input_path}/*.epub'.format(input_path=input_path)):
        txt_file = os.path.join(output_path, os.path.splitext(os.path.basename(f))[0]) + '.txt'
        if os.path.exists(txt_file):
            continue
        print(f)
        try:
            book = ebooklib.epub.read_epub(f)
        except (KeyError, AttributeError, lxml.etree.XMLSyntaxError,
                ebooklib.epub.EpubException, zipfile.BadZipFile, zipfile.zlib.error):
            # os.remove(f)
            print('removing...', f)
            continue
        metadata = book.metadata['http://purl.org/dc/elements/1.1/']
        try:
            title, author = metadata['title'][0][0], metadata['creator'][0][0]
        except KeyError:
            author, title = 'Unknown', 'Unknown'
            print('missing author/title', f)
        with open(txt_file, 'w') as out_file:
            for f in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                content = f.get_content()
                if content:
                    html = bs4.BeautifulSoup(content, 'lxml')
                    for p in html.find('body').find_all('p'):
                        p = p.get_text(separator=' ', strip=True)
                        out_file.write(p + '\n\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('output_path')
    args = parser.parse_args()
    
    main(args.path, args.output_path)
