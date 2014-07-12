#!/bin/sh

# brew install uwsgi --with-python

uwsgi --http-socket 127.0.0.1:9090 --plugin python --wsgi-file wsgi.py

#uwsgi --socket 127.0.0.1:3031 --plugin python --wsgi-file wsgi.py \
#  --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191

