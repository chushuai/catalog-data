import argparse
import bz2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='dataset', default=None, help='')
    args = parser.parse_args()

    if 'bz2' in args.dataset:
        parse_bz2(args.dataset)
    elif 'txt' in args.dataset:
        parse_txt(args.dataset)

def parse_bz2(file):
    with bz2.open(file,mode='r') as f:
        for line in f:
            line = line.decode()
            print(line)

def parse_txt(file):
    with open(file) as f:
        for line in f:
            print(line)

if __name__ == '__main__':
    main()
