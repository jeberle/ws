#!/bin/sh

# brew install uwsgi --with-python

[ $# -eq 2 ] || { echo "usage: $0 <host[:port]> <serve-dir>"; exit 1; }

uwsgi --http-socket "$1" --chdir2 "$2" --plugin python --wsgi-file wsgi.py

