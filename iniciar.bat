@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Primero crea el entorno e instala requirements.txt como indica README.md.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" src\main.py
pause
