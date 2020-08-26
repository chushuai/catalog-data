import argparse
import bz2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='dataset', default=None, help='Please enter input .bz2 file')
    args = parser.parse_args()

    if args.dataset:
        parse_bz2(args.dataset)

def parse_bz2(directory):
    data = {} # return data
    fields = [] # fields of data

    # determine the fields of the data
    filename = directory.split('/')[-1]
    if 'ptr' in filename:
        fields  = ['timestamp', 'IP_address', 'hostname']
    elif 'soa' in filename:
        fields = ['timestamp', 'IP_address', 'name', 'ns', 'mbox', 'serial', 'refresh', 'retry', 'expire', 'ttl']
    
    # parse .bz2 file
    with bz2.open(directory, mode='r') as f:
        for line in f:
            line = line.decode().strip().split()
            for i, field in enumerate(fields):
                data[field] = line[i]
            print(data)

if __name__ == '__main__':
    main()
