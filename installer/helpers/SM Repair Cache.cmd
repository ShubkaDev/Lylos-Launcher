@echo off
setlocal
set "BASE=%APPDATA%\SMLauncher"
echo Cleaning SM update temporary files...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$base=$env:APPDATA+'\SMLauncher';" ^
  "$updates=$base+'\data\updates';" ^
  "New-Item -ItemType Directory -Force $updates | Out-Null;" ^
  "Get-ChildItem $updates -Filter '*.tmp' -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue;" ^
  "Get-ChildItem $updates -Filter 'run_sm_update.cmd' -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue;" ^
  "'Done. Update cache folder: '+$updates"
echo.
echo Done. You can start SMLauncher again.
pause
endlocal
