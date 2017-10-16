set PY=%1
set DST=%2

%PY% -m venv --system-site-packages %DST%\.venv

cd /d %~dp0

%DST%\.venv\scripts\python.exe ^
    -m pip install ^
    --no-index ^
    --find-links dist ^
    -r requirements.txt
