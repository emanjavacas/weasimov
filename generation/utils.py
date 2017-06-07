
import os


def load_data(path='data/bigmama/',
              include_paragraphs=True, paragraph='<par>',
              level='token'):
    for f in os.listdir(path):
        with open(os.path.join(path, f), 'r') as infn:
            for l in infn:
                if not l.strip():
                    if include_paragraphs:
                        yield [paragraph]
                else:
                    if level == 'token':
                        yield l.strip().split()
                    elif level == 'char':
                        yield list(l.strip())
