#!/bin/bash

if [ "$1" != "--nopip" ]; then
  pip install -r requirements.txt
fi

python3 index.py