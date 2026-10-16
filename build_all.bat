@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "VIDEO_DIR=assets\video-panarama"
set "VIDEO_FILE=%VIDEO_DIR%\1.mp4"
set "VIDEO_TMP=%VIDEO_FILE%.download"
set "VIDEO_URL=https://cloud.onlysq.me/file/wSrF"
if not exist "%VIDEO_DIR%" mkdir "%VIDEO_DIR%"

rem Принимаем кэшированное видео только после проверки сигнатуры MP4.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='assets\video-panarama\1.mp4'; if (!(Test-Path -LiteralPath $p -PathType Leaf)) { exit 1 }; $s=[IO.File]::OpenRead($p); try { $b=New-Object byte[] 12; $n=$s.Read($b,0,12); if ($n -lt 12 -or [Text.Encoding]::ASCII.GetString($b,4,4) -ne 'ftyp') { exit 1 } } finally { $s.Dispose() }; exit 0"
if not errorlevel 1 goto :video_ready

del /q "%VIDEO_TMP%" >nul 2>&1
echo Загружаю видео с OnlySQ...
curl.exe --fail --location --show-error --retry 2 --connect-timeout 20 --output "%VIDEO_TMP%" "%VIDEO_URL%"
if errorlevel 1 (
    del /q "%VIDEO_TMP%" >nul 2>&1
    goto :manual_video
)

rem Скачивание может вернуть HTML вместо MP4. Проверяем временный файл,
rem а исходный файл заменяем только после успешной проверки.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='assets\video-panarama\1.mp4.download'; if (!(Test-Path -LiteralPath $p -PathType Leaf)) { exit 1 }; $s=[IO.File]::OpenRead($p); try { $b=New-Object byte[] 12; $n=$s.Read($b,0,12); if ($n -lt 12 -or [Text.Encoding]::ASCII.GetString($b,4,4) -ne 'ftyp') { exit 1 } } finally { $s.Dispose() }; exit 0"
if errorlevel 1 (
    echo Ошибка: OnlySQ вернул файл, который не распознан как MP4.
    del /q "%VIDEO_TMP%" >nul 2>&1
    goto :manual_video
)
move /y "%VIDEO_TMP%" "%VIDEO_FILE%" >nul
if errorlevel 1 (
    echo Ошибка: не удалось сохранить скачанное видео в "%VIDEO_FILE%".
    del /q "%VIDEO_TMP%" >nul 2>&1
    goto :manual_video
)

:video_ready
echo Видео проверено: "%VIDEO_FILE%"
goto :python_check

:manual_video
echo.
echo OnlySQ не предоставил корректный MP4 для прямого скачивания.
echo Открываю ссылку. Сохрани видео как "%VIDEO_FILE%" и нажми любую клавишу.
start "" "%VIDEO_URL%"
pause
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='assets\video-panarama\1.mp4'; if (!(Test-Path -LiteralPath $p)) { exit 1 }; $b=[IO.File]::ReadAllBytes((Resolve-Path $p)); if ($b.Length -lt 12 -or [Text.Encoding]::ASCII.GetString($b,4,4) -ne 'ftyp') { exit 1 }; exit 0"
if errorlevel 1 (
    echo [ОШИБКА] Корректный MP4 не найден по пути "%VIDEO_FILE%".
    pause
    exit /b 1
)

goto :video_ready


:python_check
echo.
echo Ely.by OAuth: понадобится только публичный Client ID, секрет в desktop-сборку не добавляется.
echo В регистрации выбери тип Website и укажи Redirect URI: http://127.0.0.1:8089/
start "" "https://account.ely.by/dev/applications/new"
set /p "SM_ELY_CLIENT_ID=Введи Client ID созданного приложения: "
if not defined SM_ELY_CLIENT_ID goto :oauth_error
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $id=$env:SM_ELY_CLIENT_ID.Trim(); if ([string]::IsNullOrWhiteSpace($id)) { exit 1 }; $secure=Read-Host 'Введи Client Secret (ввод скрыт)' -AsSecureString; $ptr=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure); try { $secret=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr); if ([string]::IsNullOrWhiteSpace($secret)) { exit 1 }; $settingsDir=Join-Path $env:APPDATA 'SMLauncher\data'; New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null; $settingsPath=Join-Path $settingsDir 'oauth_settings.json'; if (Test-Path $settingsPath) { $settings=Get-Content -Raw $settingsPath | ConvertFrom-Json } else { $settings=[pscustomobject]@{} }; $settings | Add-Member -NotePropertyName ely_client_id -NotePropertyValue $id -Force; $settings | Add-Member -NotePropertyName ely_client_secret -NotePropertyValue $secret -Force; [IO.File]::WriteAllText($settingsPath, (ConvertTo-Json -InputObject $settings -Depth 5), [Text.UTF8Encoding]::new($false)); $literal=ConvertTo-Json -InputObject $id -Compress; [IO.File]::WriteAllText('auth\oauth_config_local.py', ('ELY_CLIENT_ID = '+$literal+[Environment]::NewLine), [Text.UTF8Encoding]::new($false)) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }"
if errorlevel 1 goto :oauth_error
set "SM_ELY_CLIENT_ID="
echo Client ID записан для сборки; секрет сохранён локально в профиле Windows и не добавляется в EXE или Git.
echo.

set "PYTHON="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PYTHON=py -3"
if not defined PYTHON (
    python --version >nul 2>&1
    if not errorlevel 1 set "PYTHON=python"
)
if not defined PYTHON (
    echo [ОШИБКА] Python 3.12 или новее не найден. Установи Python и повтори сборку.
    timeout /t 10 /nobreak >nul
    exit /b 1
)

%PYTHON% -c "import sys; raise SystemExit(0 if sys.version_info >= (3,12) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Нужен Python версии 3.12 или новее.
    timeout /t 10 /nobreak >nul
    exit /b 1
)

echo Проверка и установка зависимостей из requirements.txt...
%PYTHON% -m pip install -r requirements.txt
if errorlevel 1 goto :build_error

if exist "build\pyinstaller" rmdir /s /q "build\pyinstaller"
if exist "dist" rmdir /s /q "dist"
if exist "release" rmdir /s /q "release"
mkdir "release"

echo [1/4] Сборка LylosLauncher.exe...
%PYTHON% -m PyInstaller --noconfirm --clean --workpath build\pyinstaller build\LylosLauncher-OneFile.spec
if errorlevel 1 goto :build_error
if not exist "dist\LylosLauncher.exe" goto :build_error
copy /y "dist\LylosLauncher.exe" "release\LylosLauncher-1.0-win-x64.exe" >nul
if errorlevel 1 goto :build_error

echo [2/4] Сборка LylosUpdater.exe...
%PYTHON% -m PyInstaller --noconfirm --clean --workpath build\pyinstaller build\LylosUpdater.spec
if errorlevel 1 goto :build_error
if not exist "dist\LylosUpdater.exe" goto :build_error

echo [3/4] Сборка LylosUninstaller.exe...
%PYTHON% -m PyInstaller --noconfirm --clean --workpath build\pyinstaller build\LylosUninstaller.spec
if errorlevel 1 goto :build_error
if not exist "dist\LylosUninstaller.exe" goto :build_error

echo [4/4] Сборка LylosSetup.exe...
%PYTHON% -m PyInstaller --noconfirm --clean --workpath build\pyinstaller build\LylosSetup.spec
if errorlevel 1 goto :build_error
if not exist "dist\LylosSetup.exe" goto :build_error

echo.
echo [ГОТОВО] EXE-файлы находятся в папке dist.
echo Установщик: dist\LylosSetup.exe
pause
exit /b 0

:oauth_error
echo.
echo [ОШИБКА] Client ID не задан или не удалось сохранить локальную OAuth-конфигурацию.
pause
exit /b 1

:build_error
echo.
echo [ОШИБКА] Загрузка зависимостей или сборка завершилась с ошибкой.
pause
exit /b 1
