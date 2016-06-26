; InnoSetup script for creating installable Windows package from built app.

[Setup]
AppName=FMIDownloader
AppVersion=0.9
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
Source: "build/exe.win32-3.5/OHJEKIRJA.pdf"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\FMIDownloader"; Filename: "{app}\FMIDownloader.exe"
Name: "{group}\Käyttöohje"; Filename: "{app}\OHJEKIRJA.pdf"
