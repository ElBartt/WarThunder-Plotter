@echo off
setlocal

set ROOT=%~dp0
cd /d "%ROOT%"

if not exist "%ROOT%\.venv" (
  py -3 -m venv "%ROOT%\.venv"
)

call "%ROOT%\.venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r "%ROOT%\requirements.txt"

echo.
echo Setup termine. Pour capturer en continu :
echo   python app.py capture
echo Pour lancer l'interface :
echo   python app.py serve

endlocal
