#!/bin/sh

# brew install uwsgi --with-python

socket=${1:-127.0.0.1:9090}
srvdir=${2:-.}
shift 2

uwsgi --http-socket "$socket" --chdir2 "$srvdir" --log-micros \
  --master --processes 2 \
  --plugin python --wsgi-file wsgi.py \
  --plugin router_cache \
  --cache2 'name=cache1,items=100' \
  --route '\.css$ cache:key=${REQUEST_URI},name=cache1,content_type=text/css' \
  --route '\.png$ cache:key=${REQUEST_URI},name=cache1,content_type=image/png' \
  --route '\.txt$ cache:key=${REQUEST_URI},name=cache1,content_type=text/plain; charset=utf-8' \
  --route '.* cache:key=${REQUEST_URI},name=cache1' \
  --route '.* cachestore:key=${REQUEST_URI},name=cache1,expires=15' \
  "$@"

# ./uwsgi.sh 127.0.0.1:9090 . --py-auto-reload 1

