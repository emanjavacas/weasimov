
import argparse
import os


def read_dedup_file(path):
    dups, dup = [], []
    with open(path, 'r') as infn:
        for line in infn:
            if not line.strip():
                assert len(dup) > 0
                dups.append(dup)
                dup = []
            else:
                dup.append(line.strip())
        return dups


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    args = parser.parse_args()
    
    for dups in read_dedup_file(args.path):
        for f in dups[1:]:
            os.remove(f)
