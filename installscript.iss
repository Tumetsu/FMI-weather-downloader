; -- Example1.iss --
; Demonstrates copying 3 files and creating an icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=FMI Downloader
AppVersion=0.7b
DefaultDirName={pf}\FMIDownloader
DefaultGroupName=FMIDownloader
UninstallDisplayIcon={app}\FMIDownloader.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Examples Output

[Files]
Source: "*"; DestDir: "{app}"
Source: "/platforms/*"; DestDir: "{app}\platforms"
;Source: "MyProg.chm"; DestDir: "{app}"
Source: "OHJEKIRJA.pdf"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\FMIDownloader"; Filename: "{app}\FMIDownloader.exe"
Name: "{group}\Käyttöohje"; Filename: "{app}\OHJEKIRJA.pdf"
