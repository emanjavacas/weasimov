import glob
import os
import zipfile

import bs4
import ebooklib
from ebooklib import epub
import lxml

# Extract meta info from each epub (i.e. author and title)

checked = set(f.name.replace('.txt', '') for f in os.scandir('../data/tokenized'))
entries, id = [], 1
for f in glob.glob('../data/epubs/*.epub'):
    fname = f.split('/')[-1].replace('.epub', '')
    if fname in checked:
        print(f)
        try:
            book = ebooklib.epub.read_epub(f)
        except (KeyError, AttributeError, lxml.etree.XMLSyntaxError,
                ebooklib.epub.EpubException, zipfile.BadZipFile):
            os.remove(f)
        metadata = book.metadata['http://purl.org/dc/elements/1.1/']
        title, author = metadata['title'][0][0], metadata['creator'][0][0]
        entries.append([id, f'{fname}.txt', author, title])
        id += 1

df = pd.DataFrame(entries, columns=['id', 'fname', 'author', 'title'])
df.to_csv("../data/meta.csv", sep=",", index=False)
