#! /usr/bin/env python

from sys import argv, exit

def main(fpath):
    for ln in open(fpath):
        ln = ln.rstrip()
        if not ln:
            continue
        print ln

if __name__ == '__main__':
    if len(argv) != 2:
        exit('usage %s <fpath>' % argv[0])
    main(argv[1])

