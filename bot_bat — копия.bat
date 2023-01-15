@echo off

call %~dp0venv\Scripts\activate

cd %~dp0

set TOKEN=<YOUR TELEGRAM TOKEN HERE>

python bot_kosiha.py

pause
