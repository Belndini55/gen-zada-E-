#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
    echo "[1/2] Tworzenie środowiska wirtualnego (.venv)..."
    python3 -m venv .venv
    echo "[2/2] Instalacja bibliotek z requirements.txt..."
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
fi

exec .venv/bin/python main.py "$@"
