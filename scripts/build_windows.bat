@echo off
REM Crea l'eseguibile Windows in dist\SicurCantiere\SicurCantiere.exe
REM e, se Inno Setup e' installato, l'installatore dist\SicurCantiere-<versione>-setup.exe
setlocal
cd /d "%~dp0\.."

if not exist .venv (
    py -3 -m venv .venv || goto :errore
)
call .venv\Scripts\activate.bat || goto :errore
python -m pip install --upgrade pip || goto :errore
python -m pip install -e ".[dev]" || goto :errore
python -m pytest -q || goto :errore
python scripts\genera_icona.py || goto :errore

pyinstaller --noconfirm --clean --windowed --name SicurCantiere ^
    --icon assets\sicurcantiere.ico ^
    --collect-data docx ^
    scripts\avvio.py || goto :errore

echo.
echo Eseguibile creato in dist\SicurCantiere\SicurCantiere.exe

set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist %ISCC% (
    %ISCC% installer\sicurcantiere.iss || goto :errore
    echo Installatore creato nella cartella dist.
) else (
    echo Inno Setup non trovato: installatore non creato.
    echo Per l'associazione dei file .scs installare Inno Setup 6 e rilanciare.
)
exit /b 0

:errore
echo.
echo Build non riuscita.
exit /b 1
