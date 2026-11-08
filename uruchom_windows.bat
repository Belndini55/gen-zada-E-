@echo off
chcp 65001 >nul
title Generator Zadan E8 - Matematyka (CKE)
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/2] Tworzenie lokalnego srodowiska Python ^(.venv^)...
    python -m venv .venv
    if errorlevel 1 (
        echo Blad: Nie znaleziono programu Python. Zainstaluj Python 3.10+ z https://www.python.org/ ^(zaznacz Add Python to PATH^).
        pause
        exit /b 1
    )
    echo [2/2] Instalowanie wymaganych bibliotek ^(PyQt6, reportlab, matplotlib, pypdfium2^)...
    .venv\Scripts\pip install --upgrade pip
    .venv\Scripts\pip install -r requirements.txt
)

start "" ".venv\Scripts\pythonw.exe" main.py
