; Installatore Windows di SicurCantiere (Inno Setup 6: https://jrsoftware.org/isinfo.php)
; Compilare dopo PyInstaller: iscc installer\sicurcantiere.iss
; Crea il collegamento nel menu Start e associa i file .scs al programma,
; così un doppio clic su un cantiere lo apre direttamente.

#define Nome "SicurCantiere"
#define Versione "0.3.0"
#define Eseguibile "SicurCantiere.exe"

[Setup]
AppId={{6B1F2C3E-5A7D-4E8B-9C0D-53C1CA171E20}
AppName={#Nome}
AppVersion={#Versione}
AppPublisher={#Nome}
DefaultDirName={autopf}\{#Nome}
DefaultGroupName={#Nome}
OutputDir=..\dist
OutputBaseFilename=SicurCantiere-{#Versione}-setup
SetupIconFile=..\assets\sicurcantiere.ico
UninstallDisplayIcon={app}\{#Eseguibile}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ChangesAssociations=yes
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "italiano"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "Crea un'icona sul desktop"; GroupDescription: "Icone aggiuntive:"
Name: "associa"; Description: "Apri i file .scs con {#Nome}"; GroupDescription: "Associazione file:"

[Files]
Source: "..\dist\SicurCantiere\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#Nome}"; Filename: "{app}\{#Eseguibile}"
Name: "{autodesktop}\{#Nome}"; Filename: "{app}\{#Eseguibile}"; Tasks: desktopicon

[Registry]
; Associazione dell'estensione .scs (per l'utente o per tutti, secondo la modalità di installazione).
Root: HKA; Subkey: "Software\Classes\.scs"; ValueType: string; ValueName: ""; ValueData: "SicurCantiere.Progetto"; Flags: uninsdeletevalue; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.Progetto"; ValueType: string; ValueName: ""; ValueData: "Cantiere SicurCantiere"; Flags: uninsdeletekey; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.Progetto\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#Eseguibile},0"; Tasks: associa
Root: HKA; Subkey: "Software\Classes\SicurCantiere.Progetto\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#Eseguibile}"" ""%1"""; Tasks: associa

[Run]
Filename: "{app}\{#Eseguibile}"; Description: "Avvia {#Nome}"; Flags: nowait postinstall skipifsilent
