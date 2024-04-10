#!/bin/sh
# startup.sh

cd ~/potentiostat-api || exit
git pull
source env/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
