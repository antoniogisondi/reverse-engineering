; Installatore Windows della famiglia SicurCantiere (Inno Setup 6: https://jrsoftware.org/isinfo.php)
; Compilare dopo PyInstaller: iscc installer\sicurcantiere.iss
; L'utente sceglie quali programmi installare; ogni programma apre con un
; doppio clic i propri file: .scs (PSC), .spo (POS), .spm (PiMUS).

#define Versione "0.7.0"

[Setup]
AppId={{6B1F2C3E-5A7D-4E8B-9C0D-53C1CA171E20}
AppName=SicurCantiere
AppVersion={#Versione}
AppPublisher=SicurCantiere
DefaultDirName={autopf}\SicurCantiere
DefaultGroupName=SicurCantiere
OutputDir=..\dist
OutputBaseFilename=SicurCantiere-{#Versione}-setup
SetupIconFile=..\assets\sicurcantiere-pos.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ChangesAssociations=yes
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "italiano"; MessagesFile: "compiler:Languages\Italian.isl"

[Types]
Name: "completa"; Description: "Tutti i programmi"
Name: "personalizzata"; Description: "Scelta dei programmi"; Flags: iscustom

[Components]
Name: "pos"; Description: "SicurCantiere POS - piano operativo di sicurezza"; Types: completa personalizzata
Name: "psc"; Description: "SicurCantiere PSC - piano di sicurezza e coordinamento"; Types: completa
Name: "pimus"; Description: "SicurCantiere PiMUS - ponteggi"; Types: completa

[Tasks]
Name: "desktopicon"; Description: "Crea le icone sul desktop"; GroupDescription: "Icone aggiuntive:"
Name: "associa"; Description: "Apri i file dei cantieri con doppio clic"; GroupDescription: "Associazione file:"

[Files]
Source: "..\dist\SicurCantiere PSC\*"; DestDir: "{app}\PSC"; Components: psc; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\SicurCantiere POS\*"; DestDir: "{app}\POS"; Components: pos; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\SicurCantiere PiMUS\*"; DestDir: "{app}\PiMUS"; Components: pimus; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SicurCantiere PSC"; Filename: "{app}\PSC\SicurCantiere PSC.exe"; Components: psc
Name: "{group}\SicurCantiere POS"; Filename: "{app}\POS\SicurCantiere POS.exe"; Components: pos
Name: "{group}\SicurCantiere PiMUS"; Filename: "{app}\PiMUS\SicurCantiere PiMUS.exe"; Components: pimus
Name: "{autodesktop}\SicurCantiere PSC"; Filename: "{app}\PSC\SicurCantiere PSC.exe"; Components: psc; Tasks: desktopicon
Name: "{autodesktop}\SicurCantiere POS"; Filename: "{app}\POS\SicurCantiere POS.exe"; Components: pos; Tasks: desktopicon
Name: "{autodesktop}\SicurCantiere PiMUS"; Filename: "{app}\PiMUS\SicurCantiere PiMUS.exe"; Components: pimus; Tasks: desktopicon

[Registry]
; .scs -> PSC
Root: HKA; Subkey: "Software\Classes\.scs"; ValueType: string; ValueName: ""; ValueData: "SicurCantiere.PSC"; Flags: uninsdeletevalue; Components: psc; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.PSC"; ValueType: string; ValueName: ""; ValueData: "Cantiere PSC"; Flags: uninsdeletekey; Components: psc; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.PSC\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\PSC\SicurCantiere PSC.exe,0"; Components: psc; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.PSC\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\PSC\SicurCantiere PSC.exe"" ""%1"""; Components: psc; Tasks: associa
; .spo -> POS
Root: HKA; Subkey: "Software\Classes\.spo"; ValueType: string; ValueName: ""; ValueData: "SicurCantiere.POS"; Flags: uninsdeletevalue; Components: pos; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.POS"; ValueType: string; ValueName: ""; ValueData: "Cantiere POS"; Flags: uninsdeletekey; Components: pos; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.POS\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\POS\SicurCantiere POS.exe,0"; Components: pos; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.POS\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\POS\SicurCantiere POS.exe"" ""%1"""; Components: pos; Tasks: associa
; .spm -> PiMUS
Root: HKA; Subkey: "Software\Classes\.spm"; ValueType: string; ValueName: ""; ValueData: "SicurCantiere.PiMUS"; Flags: uninsdeletevalue; Components: pimus; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.PiMUS"; ValueType: string; ValueName: ""; ValueData: "Ponteggi PiMUS"; Flags: uninsdeletekey; Components: pimus; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.PiMUS\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\PiMUS\SicurCantiere PiMUS.exe,0"; Components: pimus; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.PiMUS\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\PiMUS\SicurCantiere PiMUS.exe"" ""%1"""; Components: pimus; Tasks: associa

[Run]
Filename: "{app}\POS\SicurCantiere POS.exe"; Description: "Avvia SicurCantiere POS"; Components: pos; Flags: nowait postinstall skipifsilent
