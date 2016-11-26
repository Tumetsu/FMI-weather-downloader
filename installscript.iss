; InnoSetup script for creating installable Windows package from built app.

[Setup]
AppName=FMIDownloader
AppVersion=0.15.1
DefaultDirName={pf}\FMIDownloader
DefaultGroupName=FMIDownloader
UninstallDisplayIcon={app}\FMIDownloader.exe
Compression=lzma2
SolidCompression=yes
OutputDir="build"
UsePreviousAppDir=no
OutputBaseFilename=FMIDownloader_Setup

[Files]
Source: "build/exe.win32-3.5/*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\FMIDownloader"; Filename: "{app}\FMIDownloader.exe"

[Run]
Filename: http://tumetsu.github.io/FMI-weather-downloader/quickstart/quickstart.html; Description: "Read quickstart"; Flags: postinstall shellexec
Filename: {app}\FMIDownloader.exe; Description: {cm:LaunchProgram,FMIDownloader}; Flags: nowait postinstall skipifsilent
