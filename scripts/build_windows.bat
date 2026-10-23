@echo off
REM Compila i programmi SicurCantiere (PSC, POS, PiMUS) con Nuitka in dist\SicurCantiere\ e, se Inno Setup 6
REM e' installato, crea l'installatore dist\SicurCantiere-<versione>-setup.exe
REM
REM Nuitka traduce il codice Python in C e lo compila: l'eseguibile non contiene il sorgente e non si
REM decompila come un programma Python impacchettato. I tre programmi sono copie dello stesso eseguibile
REM nella stessa cartella (l'edizione dipende dal nome del file): le librerie si installano una volta sola.
setlocal
cd /d "%~dp0\.."

if not exist .venv (
    py -3 -m venv .venv || goto :errore
)
call .venv\Scripts\activate.bat || goto :errore
python -m pip install --upgrade pip || goto :errore
REM versioni esatte con impronta (hash): un pacchetto alterato sull'indice non viene installato
python -m pip install --require-hashes -r requisiti\build.txt || goto :errore
python -m pip install --no-deps -e . || goto :errore
python -m pytest -q || goto :errore
python scripts\genera_icona.py || goto :errore

for /f "tokens=2 delims==" %%v in ('findstr /b "__version__" sicurcantiere\__init__.py') do set VERSIONE=%%~v
set VERSIONE=%VERSIONE: =%
set VERSIONE=%VERSIONE:"=%
echo Versione %VERSIONE%

REM traduzioni italiane di Qt (Sì/No/Annulla...): Nuitka le include solo con QtWebEngine, qui si aggiungono
for /f "delims=" %%t in ('python -c "from PySide6.QtCore import QLibraryInfo as L; print(L.path(L.LibraryPath.TranslationsPath))"') do set TRADUZIONI=%%t

if exist build\nuitka rmdir /s /q build\nuitka
if exist dist\SicurCantiere rmdir /s /q dist\SicurCantiere
python -m nuitka --standalone --assume-yes-for-downloads --msvc=latest ^
    --enable-plugin=pyside6 --include-qt-plugins=sensible ^
    --windows-console-mode=disable --windows-icon-from-ico=assets\sicurcantiere.ico ^
    --company-name=SicurCantiere --product-name=SicurCantiere ^
    --file-version=%VERSIONE% --product-version=%VERSIONE% --file-description="SicurCantiere" ^
    --include-package=sicurcantiere --include-package=sicur_license ^
    --include-data-dir=sicurcantiere\risorse=sicurcantiere\risorse ^
    "--include-data-files=%TRADUZIONI%\qtbase_it.qm=traduzioni\qtbase_it.qm" ^
    "--include-data-files=%TRADUZIONI%\qt_it.qm=traduzioni\qt_it.qm" ^
    --nofollow-import-to=openai,anthropic,cryptography,pytest,flask,licenze,tests ^
    --output-dir=build\nuitka --output-filename=SicurCantiere.exe ^
    scripts\avvio.py || goto :errore

if not exist dist mkdir dist
move build\nuitka\avvio.dist dist\SicurCantiere || goto :errore
for %%p in (PSC POS PiMUS) do (
    copy /y dist\SicurCantiere\SicurCantiere.exe "dist\SicurCantiere\SicurCantiere %%p.exe" >nul || goto :errore
)
del dist\SicurCantiere\SicurCantiere.exe
echo Creati i programmi in dist\SicurCantiere

set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist %ISCC% (
    %ISCC% installer\sicurcantiere.iss || goto :errore
    echo Installatore creato nella cartella dist.
) else (
    echo Inno Setup non trovato: installatore non creato.
    echo Per l'associazione dei file installare Inno Setup 6 e rilanciare.
)
exit /b 0

:errore
echo.
echo Build non riuscita.
exit /b 1
