@echo off
setlocal
cd /d "%~dp0"
if not exist "SMLauncher.exe" (
  echo SMLauncher.exe not found in %CD%
  pause
  exit /b 1
)
start "" "%CD%\SMLauncher.exe" --open-updates
endlocal
