#!/bin/bash

usepip="y"
port=8080

for arg in "$@"; do
  if [[ "$arg" == *"--nopip"* ]]; then
    usepip="n"
  elif [[ "$arg" == *"--port"* ]]; then
    shift
    if [ $# -gt 0 ]; then
      port="$1"
    else
      echo "Error: --port requires an argument"
      exit 1
    fi
  fi
  shift
done

if [ "$usepip" != "n" ]; then
  pip install -r requirements.txt
fi

python3 index.py "$port"