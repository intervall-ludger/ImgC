[Setup]
AppId={{3F96B359-E707-4242-42B0-427B28D4958A}}
AppName=Image Converter
AppVersion=1.0
;AppVerName=Image Converter 1.0
AppPublisher=Karl Ludger Radke
DefaultDirName={pf}\Image Converter
DefaultGroupName=Image Converter
OutputBaseFilename=ImageConverterSetup
Compression=lzma
LicenseFile=LICENSE
SolidCompression=yes
SetupIconFile=icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ImageConverter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Image Converter"; Filename: "{app}\ImageConverter.exe"
Name: "{commondesktop}\Image Converter"; Filename: "{app}\ImageConverter.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ImageConverter.exe"; Description: "{cm:LaunchProgram,Image Converter}"; Flags: nowait postinstall skipifsilent
