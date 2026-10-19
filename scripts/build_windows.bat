@echo off
REM Crea gli eseguibili Windows dei programmi SicurCantiere (PSC, POS, PiMUS) in dist\
REM e, se Inno Setup 6 e' installato, l'installatore dist\SicurCantiere-<versione>-setup.exe
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

call :programma PSC psc || goto :errore
call :programma POS pos || goto :errore
call :programma PiMUS pimus || goto :errore

set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist %ISCC% (
    %ISCC% installer\sicurcantiere.iss || goto :errore
    echo Installatore creato nella cartella dist.
) else (
    echo Inno Setup non trovato: installatore non creato.
    echo Per l'associazione dei file installare Inno Setup 6 e rilanciare.
)
exit /b 0

:programma
REM %1 = nome visibile, %2 = chiave dell'edizione
pyinstaller --noconfirm --clean --windowed --name "SicurCantiere %1" ^
    --icon assets\sicurcantiere-%2.ico ^
    --collect-data docx ^
    scripts\avvio_%2.py || exit /b 1
echo Creato dist\SicurCantiere %1\SicurCantiere %1.exe
exit /b 0

:errore
echo.
echo Build non riuscita.
exit /b 1
