@echo off
cd /d "%~dp0"
set "LOCAL_PY=%~dp0.conda\python.exe"
set "SIBLING_PY=%~dp0..\GUI\.conda\python.exe"

if exist "%LOCAL_PY%" (
    "%LOCAL_PY%" -c "from PySide6.QtWidgets import QApplication; import requests" >nul 2>nul
    if not errorlevel 1 (
        "%LOCAL_PY%" main.py
        exit /b
    )
)

if exist "%SIBLING_PY%" (
    "%SIBLING_PY%" main.py
    exit /b
)

python -c "from PySide6.QtWidgets import QApplication; import requests" >nul 2>nul
if errorlevel 1 (
    python -m pip install -r requirements.txt
)

python main.py
