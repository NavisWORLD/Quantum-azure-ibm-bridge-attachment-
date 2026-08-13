#define MyAppName "QBT Desktop"
#define MyAppVersion "0.4.0"
#define MyAppPublisher "Cory Shane Davis / NavisWORLD"
#define MyAppExeName "QBT-Desktop.exe"

[Setup]
AppId={{B6C95C87-D7C9-43B3-BCE1-7FC9A27D8040}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\QBT
DefaultGroupName=QBT
AllowNoIcons=yes
OutputDir=..\..\release-artifacts
OutputBaseFilename=QBT-Windows-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=..\..\LICENSE
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\..\dist\QBT-Desktop.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\target\release\qbt-rs.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\DISTRIBUTION.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\QBT Desktop"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\QBT Desktop"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\QBT Rust CLI"; Filename: "{cmd}"; Parameters: "/K ""{app}\qbt-rs.exe"" --help"; WorkingDir: "{app}"
Name: "{group}\Uninstall QBT"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch QBT Desktop"; Flags: nowait postinstall skipifsilent
