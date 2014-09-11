#! /usr/bin/env bash

set -e
rm -r _site
mkdir _site
wget -r --no-host-directories -P _site http://localhost:9090
find _site -type f ! -name '*.*' -print0 | xargs -0 -n 1 bash -c 'mv $0 $0.html'
