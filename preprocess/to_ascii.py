import glob
import unidecode
import sys

if __name__ == '__main__':
    input_directory = sys.argv[1]
    for fname in glob.glob(f'{input_directory}/*.txt'):
        with open(fname) as infile:
            data = infile.read()
        ascii_data = unidecode(data)
        with open(f'{output_directory}/{fname}', 'w') as outfile:
            outfile.write(ascii_data)
