@echo off
REM Crea l'eseguibile Windows in dist\SicurCantiere\SicurCantiere.exe
setlocal
cd /d "%~dp0\.."

if not exist .venv (
    py -3 -m venv .venv || goto :errore
)
call .venv\Scripts\activate.bat || goto :errore
python -m pip install --upgrade pip || goto :errore
python -m pip install -e ".[dev]" || goto :errore
python -m pytest -q || goto :errore

pyinstaller --noconfirm --clean --windowed --name SicurCantiere ^
    --collect-data docx ^
    scripts\avvio.py || goto :errore

echo.
echo Eseguibile creato in dist\SicurCantiere\SicurCantiere.exe
exit /b 0

:errore
echo.
echo Build non riuscita.
exit /b 1
