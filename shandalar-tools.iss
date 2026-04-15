[Setup]
AppName=Shandalar Tools
AppVersion=1.0
AppPublisher=Jennifer Mortensen
DefaultDirName={userdocs}\Shandalar Tools
DefaultGroupName=Shandalar Tools
OutputDir=installer
OutputBaseFilename=ShandalarToolsSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
InfoBeforeFile=installer_note.txt

[Files]
Source: "dist\shandalar-tools.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\readme.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\config.csv"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\user_banned.csv"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\config_templates.zip"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\data\*"; DestDir: "{app}\data"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\Shandalar Tools"; Filename: "{app}\shandalar-tools.exe"
Name: "{group}\Uninstall Shandalar Tools"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\shandalar-tools.exe"; Description: "Run Shandalar Tools"; Flags: nowait postinstall skipifsilent