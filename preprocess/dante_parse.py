import inspect
import os
import lxml.etree
import pandas as pd


def nur_tree(fpath: str) -> dict:
    tree = {}
    anchor, depth = [None, None, None], 0
    for line in open(fpath):
        depth = line.count('\t')
        code, description = line.strip().split(' ', 1)
        if depth > 0:
            tree[code] = {'description': description, 'parent': anchor[depth - 1]}
        else:
            tree[code] = {'description': description, 'parent': None}
        anchor[depth] = code
    return tree


class DanteMeta:
    def __init__(self, fname, nur_tree, expand_categories=False):
        self.fname = fname
        self.tree = lxml.etree.parse(fname.path)
        self.ns = {'ns': 'http://www.editeur.org/onix/3.0/reference'}
        self.nur_tree = nur_tree
        self.expand_categories = expand_categories

    def get_fname(self):
        return {'txt_file': self.fname.name}

    def in_dante(self):
        if not hasattr(self, 'n_products'):
            self.n_products = int(self.tree.find('//ns:NrOfProducts', namespaces=self.ns).text)
        return self.n_products > 0

    def get_record_id(self):
        if not hasattr(self, 'record_id'):
            self.record_id = {'record_id': self.tree.find('//ns:RecordReference', namespaces=self.ns).text}
        return self.record_id

    def get_author(self):
        if not hasattr(self, 'author'):
            try:
                self.author = next({'author:id': contributor.find('ns:NameIdentifier/ns:NameIDType/ns:IDValue', namespaces=self.ns).text,
                    #  'author:firstname': contributor.find('ns:NamesBeforeKey', namespaces=self.ns).text,
                     'author:lastname': contributor.find('ns:KeyNames', namespaces=self.ns).text}
                     for contributor in self.tree.xpath('//ns:Contributor', namespaces=self.ns)
                     if contributor.find('ns:ContributorRole', namespaces=self.ns).text == 'A01')
            except StopIteration:
                self.author = ''
        return self.author

    def get_title(self):
        if not hasattr(self, 'title'):
            self.title = next({'title:detail': title.find('ns:TitleElement/ns:TitleText', namespaces=self.ns).text}
                for title in self.tree.xpath('//ns:TitleDetail', namespaces=self.ns)
                if title.find('ns:TitleType', namespaces=self.ns).text == '01')
        return self.title

    def get_subject(self):
        if not hasattr(self, 'subject'):
            self.subject = next({'subject': subject.find('ns:SubjectCode', namespaces=self.ns).text}
                for subject in self.tree.xpath('//ns:Subject', namespaces=self.ns)
                if subject.find('ns:SubjectSchemeIdentifier', namespaces=self.ns).text == '32')
        return self.subject

    def _get_categories(self, code):
        results = [self.nur_tree[code]['description']]
        parent = self.nur_tree[code]['parent']
        if self.expand_categories and parent is not None:
            results += self._get_categories(parent)
        return results

    def get_categories(self):
        categories = self._get_categories(self.get_subject()['subject'])
        return {'categories': ','.join(categories)}

    def get_language(self):
        if not hasattr(self, 'language'):
            self.language = {'language': self.tree.find('//ns:LanguageCode', namespaces=self.ns).text}
        return self.language

    def meta_info(self):
        meta = {}
        if self.in_dante():
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
                if name.startswith('get_'):
                    meta.update(method())
        return meta


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str)
    parser.add_argument('--output_file', type=str)
    args = parser.parse_args()

    dicts = []
    nur = nur_tree('nur.txt')
    for fname in os.scandir(args.input_dir):
        if fname.name.endswith('.xml'):
            print(fname)
            tree = DanteMeta(fname, nur, expand_categories=True)
            dicts.append(tree.meta_info())
    df = pd.DataFrame(dicts).fillna('').to_csv(args.output_file, index=False)
