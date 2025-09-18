@echo off

if "%1" neq "--nopip" (
  pip install -r requirements.txt
)

python index.py