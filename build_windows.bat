@echo off
setlocal

set APP_NAME=WarThunderPlotter
set DIST_DIR=dist

echo === Build Windows portable EXE ===
py -m pip install -r requirements.txt
py -m pip install pyinstaller

py -m PyInstaller --name "%APP_NAME%" --onefile --noconsole --add-data "templates;templates" --add-data "static;static" app.py

if exist "%DIST_DIR%\%APP_NAME%.exe" (
    move /y "%DIST_DIR%\%APP_NAME%.exe" "%DIST_DIR%\%APP_NAME%-portable.exe" >nul
)

echo.
echo Build complete: %DIST_DIR%\%APP_NAME%-portable.exe
endlocal
