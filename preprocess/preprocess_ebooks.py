import glob
import os
import zipfile

import bs4
import ebooklib
from ebooklib import epub
import lxml

# convert epubs into txt files. 

for f in glob.glob('../data/epubs/*.epub'):
    print(f)
    try:
        book = ebooklib.epub.read_epub(f)
    except (KeyError, AttributeError, lxml.etree.XMLSyntaxError,
            ebooklib.epub.EpubException, zipfile.BadZipFile):
        os.remove(f)
    metadata = book.metadata['http://purl.org/dc/elements/1.1/']
    title, author = metadata['title'][0][0], metadata['creator'][0][0]
    txt_file = os.path.join('../data/txt', os.path.splitext(os.path.basename(f))[0]) + '.txt'
    with open(txt_file, 'w') as out_file:
        for f in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = f.get_content()
            if content:
                html = bs4.BeautifulSoup(content, 'lxml')
                for p in html.find('body').find_all('p'):
                    p = p.get_text(separator=' ', strip=True)
                    out_file.write(p + '\n\n')
