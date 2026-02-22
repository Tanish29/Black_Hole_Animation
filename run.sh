#!/usr/bin/env sh
set -e

cd "$(dirname "$0")"

if [ -d ".venv" ]; then
    . .venv/bin/activate
fi

python main.py
