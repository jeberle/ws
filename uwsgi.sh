#!/bin/sh

# brew install uwsgi --with-python
# pip install -r requirements.txt
# ./uwsgi.sh 127.0.0.1:9090 . 1 --py-auto-reload 1

DIR=${0%/*}
SOCKET=${1:-127.0.0.1:9090}
SRVDIR=${2:-.}
EXPIRES=${3:-15}
shift 3

uwsgi --http-socket "$SOCKET" --chdir2 "$SRVDIR" \
  --master --processes 2 \
  --plugin python --wsgi-file "$DIR"/wsgi.py \
  --plugin router_cache \
  --cache2 'name=cache1,items=100' \
  --route '\.css$ cache:key=${REQUEST_URI},name=cache1,content_type=text/css' \
  --route '\.png$ cache:key=${REQUEST_URI},name=cache1,content_type=image/png' \
  --route '.* cache:key=${REQUEST_URI},name=cache1,content_type=text/html' \
  --route '.* cachestore:key=${REQUEST_URI},name=cache1,expires='"$EXPIRES" \
  --log-format '%(status) %(msecs) %(method) %(uri)' \
  "$@"

