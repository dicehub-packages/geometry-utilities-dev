#!/bin/bash

py=$1
dst=$2

$py -m venv --system-site-packages --symlinks "$dst/.venv"

cd `pwd`/install

"$dst/.venv/bin/python3" \
    -m pip install \
    --no-index \
    --find-links dist \
    -r requirements.txt
