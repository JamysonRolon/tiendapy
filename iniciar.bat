@echo off
rem Oculta los comandos para mostrar solamente los mensajes del programa.
rem Se ubica en la carpeta donde esta guardado este archivo .bat.
cd /d "%~dp0"
rem Comprueba que exista el Python del entorno virtual antes de intentar abrirlo.
if not exist ".venv\Scripts\python.exe" (
    echo Primero crea el entorno e instala requirements.txt como indica README.md.
    pause
    exit /b 1
)
rem Ejecuta el menu con el Python y las dependencias del proyecto.
".venv\Scripts\python.exe" src\main.py
rem Mantiene la ventana abierta al terminar para poder leer los mensajes.
pause
