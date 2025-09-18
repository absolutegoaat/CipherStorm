@echo off

set usepip=y
set port=8080

:loop
if "%~1"=="" goto endloop
if "%~1"=="--nopip" (
  set usepip=n
) else if "%~1"==""--port" (
  if "%~2"=="" (
    echo Error: --port requires an argument
    exit /b 1
  )
  set port=%2
  shift
)
shift
goto loop
:endloop

if "%usepip%"=="y" (
  pip install -r requirements.txt
)

python index.py %port%