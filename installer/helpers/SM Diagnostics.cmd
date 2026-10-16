@echo off
setlocal
set "APPDIR=%~dp0"
set "BASE=%APPDATA%\SMLauncher"
set "REPORT=%BASE%\diagnostics\sm_diagnostics.txt"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='SilentlyContinue';" ^
  "$base=$env:APPDATA+'\SMLauncher';" ^
  "$report=$base+'\diagnostics\sm_diagnostics.txt';" ^
  "New-Item -ItemType Directory -Force (Split-Path $report) | Out-Null;" ^
  "'SMLauncher diagnostics' | Set-Content $report -Encoding UTF8;" ^
  "'Date: ' + (Get-Date) | Add-Content $report -Encoding UTF8;" ^
  "'App folder: %APPDIR%' | Add-Content $report -Encoding UTF8;" ^
  "if (Test-Path '%APPDIR%SMLauncher.exe') { $f=Get-Item '%APPDIR%SMLauncher.exe'; 'EXE size: '+[math]::Round($f.Length/1MB,2)+' MB' | Add-Content $report -Encoding UTF8; 'EXE modified: '+$f.LastWriteTime | Add-Content $report -Encoding UTF8 };" ^
  "'Data folder: '+$base | Add-Content $report -Encoding UTF8;" ^
  "$log=$base+'\data\logs\latest.log'; if (Test-Path $log) { ''; '--- latest.log tail ---' | Add-Content $report -Encoding UTF8; Get-Content $log -Tail 120 | Add-Content $report -Encoding UTF8 } else { 'latest.log not found' | Add-Content $report -Encoding UTF8 };" ^
  "notepad $report"

endlocal
