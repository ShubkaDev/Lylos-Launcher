; Lylos Launcher installer
; Build with:
;   ISCC.exe /DAppVersion=1.0 installer\SMLauncher.iss

#ifndef AppVersion
#define AppVersion "1.2.1"
#endif

#define AppName "Lylos Launcher"
#define AppExeName "LylosLauncher.exe"
#define SourceExe "..\release\LylosLauncher-" + AppVersion + "-win-x64.exe"

[Setup]
AppId={{B5D3C6F2-4C92-4F01-9E4F-41B0E3B85C47}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Lylos Launcher
AppPublisherURL=https://github.com/ShubkaDev/SMLauncher
AppSupportURL=https://github.com/ShubkaDev/SMLauncher/issues
AppUpdatesURL=https://github.com/ShubkaDev/SMLauncher/releases
DefaultDirName={localappdata}\Programs\Lylos Launcher
DefaultGroupName=Lylos Launcher
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\release
OutputBaseFilename=LylosSetup-{#AppVersion}-win-x64
SetupIconFile=..\assets\LL.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
MinVersion=10.0
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Ярлыки:"; Flags: checkedonce

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "{#AppExeName}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "helpers\*.cmd"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Lylos Launcher"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{autoprograms}\Lylos Launcher - Проверить обновления"; Filename: "{app}\SM Check Updates.cmd"; WorkingDir: "{app}"
Name: "{autoprograms}\Lylos Launcher - Диагностика"; Filename: "{app}\SM Diagnostics.cmd"; WorkingDir: "{app}"
Name: "{autoprograms}\Lylos Launcher - Очистить кэш обновлений"; Filename: "{app}\SM Repair Cache.cmd"; WorkingDir: "{app}"
Name: "{autoprograms}\Lylos Launcher - Сайт"; Filename: "{app}\Open SM Website.cmd"; WorkingDir: "{app}"
Name: "{autodesktop}\Lylos Launcher"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autoprograms}\Удалить Lylos Launcher"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Запустить Lylos Launcher"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; User data is intentionally kept in %APPDATA%\SMLauncher.
; Do not delete instances, accounts, logs or downloaded packs automatically.

[Code]
const
  AppUninstallKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{B5D3C6F2-4C92-4F01-9E4F-41B0E3B85C47}_is1';

procedure StopRunningSMLauncher();
var
  ResultCode: Integer;
begin
  Log('Stopping running SMLauncher processes before install/update.');
  Exec(
    ExpandConstant('{cmd}'),
    '/C taskkill /IM "{#AppExeName}" /T /F >NUL 2>NUL',
    '',
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode
  );
  Log('taskkill SMLauncher exit code: ' + IntToStr(ResultCode));
  Sleep(1200);
end;

function ExtractExeAndParams(CommandLine: string; var ExePath: string; var Params: string): Boolean;
var
  EndQuote: Integer;
  SpacePos: Integer;
begin
  CommandLine := Trim(CommandLine);
  ExePath := '';
  Params := '';

  if CommandLine = '' then
  begin
    Result := False;
    Exit;
  end;

  if Copy(CommandLine, 1, 1) = '"' then
  begin
    EndQuote := Pos('"', Copy(CommandLine, 2, MaxInt));
    if EndQuote > 0 then
    begin
      ExePath := Copy(CommandLine, 2, EndQuote - 1);
      Params := Trim(Copy(CommandLine, EndQuote + 2, MaxInt));
    end;
  end
  else
  begin
    SpacePos := Pos(' ', CommandLine);
    if SpacePos > 0 then
    begin
      ExePath := Copy(CommandLine, 1, SpacePos - 1);
      Params := Trim(Copy(CommandLine, SpacePos + 1, MaxInt));
    end
    else
    begin
      ExePath := CommandLine;
    end;
  end;

  Result := ExePath <> '';
end;

procedure RunPreviousUninstaller(RootKey: Integer);
var
  UninstallCommand: string;
  ExePath: string;
  Params: string;
  ResultCode: Integer;
begin
  if RegQueryStringValue(RootKey, AppUninstallKey, 'QuietUninstallString', UninstallCommand) or
     RegQueryStringValue(RootKey, AppUninstallKey, 'UninstallString', UninstallCommand) then
  begin
    if ExtractExeAndParams(UninstallCommand, ExePath, Params) and FileExists(ExePath) then
    begin
      Log('Removing previous SMLauncher version: ' + ExePath);
      Params := Trim(Params + ' /VERYSILENT /SUPPRESSMSGBOXES /NORESTART');
      Exec(ExePath, Params, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Log('Previous SMLauncher uninstaller exit code: ' + IntToStr(ResultCode));
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  StopRunningSMLauncher();
  RunPreviousUninstaller(HKCU);
  RunPreviousUninstaller(HKLM);
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    StopRunningSMLauncher();
  end;
end;
