"""SMLauncher uninstaller — full SM-styled window that removes the app cleanly.

Resolves the real install folder from the Windows uninstall registry entry
(InstallLocation), removes shortcuts, data (%APPDATA%\\SMLauncher) and the
Settings → Apps registration entry, then deletes the install folder itself,
including this running executable.

Deletion of the running EXE is deferred to a detached hidden PowerShell helper
that waits until this process has exited, then force-removes the leftover
folders and the uninstaller EXE itself — no console window is ever shown.
"""
from __future__ import annotations

import base64
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

VERSION = "1.0"
APP_NAME = "Lylos Launcher"
LEGACY_APP_NAME = "Lylos-Launcher"
EXE_NAME = "Удалить LylosLauncher.exe"
UNINSTALL_NAME = "Удалить Lylos Launcher.exe"
# Записи в «Настройки → Приложения» Windows. Установщик пишет ключ SMLauncher,
# поэтому удалятор должен почистить именно его, а заодно и старые варианты.
UNINSTALL_REG_KEYS = (
    r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SMLauncher",
    r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Lylos-Launcher",
    r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Lylos Launcher",
)
UNINSTALL_REG_KEY = UNINSTALL_REG_KEYS[0]

APPDATA_DIR = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
APP_DIR = APPDATA_DIR / APP_NAME
LEGACY_APP_DIR = APPDATA_DIR / LEGACY_APP_NAME

STYLE = """
* { font-family: "Segoe UI"; color: #E5E7EB; font-size: 13px; outline: none; }
QWidget { background-color: transparent; }
QMainWindow, #Root {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0B0E1A, stop:0.5 #151230, stop:1 #0A2430);
}
QLabel#Title { font-size: 24px; font-weight: 800; color: #F5F3FF; }
QLabel#Muted { color: #94A3B8; font-size: 12px; }
QLabel#WarnTitle { font-size: 16px; font-weight: 800; color: #FCA5A5; }
QFrame#Card {
  background-color: rgba(20, 25, 48, 0.72);
  border: 1px solid rgba(139, 92, 246, 0.22);
  border-radius: 18px;
}
QPushButton {
  background-color: rgba(10, 14, 28, 0.9);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
  padding: 12px 20px;
}
QPushButton:hover { border-color: #22D3EE; }
QPushButton#Primary {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8B5CF6, stop:1 #22D3EE);
  color: #0F0A1C; font-weight: 800; border: none;
}
QPushButton#Primary:hover { border: 1px solid #A5F3FC; }
QPushButton#Danger {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #B91C1C, stop:1 #F59E0B);
  color: #FFFFFF; font-weight: 800; border: none;
}
QPushButton#Danger:hover { border: 1px solid #FCA5A5; }
QPushButton:disabled { color: #64748B; background-color: rgba(15, 23, 42, 0.45); }
QProgressBar {
  background: rgba(255,255,255,0.08); border: none; border-radius: 6px; max-height: 10px;
}
QProgressBar::chunk {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #8B5CF6, stop:1 #22D3EE);
  border-radius: 6px;
}
"""


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[1]


def _is_sm_folder(path: Path) -> bool:
    """True if `path` looks like an SMLauncher install folder (safety guard).

    Guards against ever rmdir-ing a drive root or a system folder.
    """
    try:
        path = path.resolve()
    except Exception:
        pass
    if len(path.parts) < 3:
        return False  # never a drive root or top-level folder
    name = path.name.casefold()
    if name in {APP_NAME.casefold(), LEGACY_APP_NAME.casefold()}:
        return True
    if (path / EXE_NAME).is_file():
        return True
    if (path / UNINSTALL_NAME).is_file():
        return True
    return False


def _read_registry_values(key_path: str, names: tuple[str, ...]) -> dict[str, str]:
    """Read string values from HKCU\\key_path; missing ones are skipped."""
    out: dict[str, str] = {}
    try:
        import winreg
    except Exception:
        return out
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            for name in names:
                try:
                    value, _kind = winreg.QueryValueEx(key, name)
                    if isinstance(value, str) and value:
                        out[name] = value
                except OSError:
                    pass
    except OSError:
        pass
    return out


def resolve_install_dir() -> Path | None:
    """Locate the real install folder, preferring the registry written by SMSetup.

    PyInstaller onefile re-points sys.executable to the temp extraction dir, so
    we can never trust it here — the registry InstallLocation is authoritative.
    """
    values = _read_registry_values(
        UNINSTALL_REG_KEY, ("InstallLocation", "DisplayIcon", "UninstallString")
    )
    for value_name in ("InstallLocation", "DisplayIcon"):
        raw = values.get(value_name)
        if not raw:
            continue
        candidate = Path(raw).expanduser()
        if value_name == "DisplayIcon":
            candidate = candidate.parent
        try:
            if candidate.is_dir() and _is_sm_folder(candidate):
                return candidate
        except Exception:
            continue
    uninst_raw = values.get("UninstallString", "").strip().strip('"')
    if uninst_raw:
        candidate = Path(uninst_raw).expanduser().parent
        try:
            if candidate.is_dir() and _is_sm_folder(candidate):
                return candidate
        except Exception:
            pass
    home = Path.home()
    candidates = [
        APP_DIR,
        LEGACY_APP_DIR,
        home / "AppData" / "Local" / "Programs" / APP_NAME,
        home / "AppData" / "Local" / "Programs" / LEGACY_APP_NAME,
        home / "AppData" / "Local" / APP_NAME,
        home / "AppData" / "Local" / LEGACY_APP_NAME,
    ]
    if os.environ.get("ProgramFiles"):
        program_files = Path(os.environ["ProgramFiles"])
        candidates.extend([program_files / APP_NAME, program_files / LEGACY_APP_NAME])
    for candidate in candidates:
        try:
            if candidate.is_dir() and _is_sm_folder(candidate):
                return candidate
        except Exception:
            continue
    return None


def _delete_registry_keys(key_paths: list[str] | tuple[str, ...]) -> None:
    """Remove the uninstall registration keys (winreg, then reg.exe fallback)."""
    for key_path in key_paths:
        _delete_registry_key(key_path)


def _delete_registry_key(key_path: str) -> None:
    """Remove the uninstall registration key (winreg, then reg.exe fallback)."""
    try:
        import winreg

        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            return
        except FileNotFoundError:
            return
        except OSError:
            pass
    except Exception:
        pass
    try:
        subprocess.run(
            ["reg", "delete", f"HKCU\\{key_path}", "/f"],
            capture_output=True,
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        pass


def _iter_delete_targets(folder: Path) -> list[Path]:
    """Children of `folder` to delete (skips the running uninstaller files)."""
    if not folder.is_dir():
        return []
    try:
        running = Path(sys.executable).resolve()
    except Exception:
        running = None
    targets: list[Path] = []
    for child in list(folder.iterdir()):
        try:
            if running and child.resolve() == running:
                continue
            if child.name == UNINSTALL_NAME:
                continue
            targets.append(child)
        except Exception:
            pass
    return targets


def _running_uninstaller_exe() -> Path | None:
    """Original path of the running uninstaller EXE (from the registry).

    In a PyInstaller onefile build sys.executable points to the temp copy, so
    the real EXE that must self-delete is found via UninstallString.
    """
    values = _read_registry_values(UNINSTALL_REG_KEY, ("UninstallString",))
    raw = values.get("UninstallString", "").strip().strip('"')
    if not raw:
        return None
    candidate = Path(raw)
    try:
        if candidate.name == UNINSTALL_NAME and (candidate.exists() or candidate.parent.is_dir()):
            return candidate
    except Exception:
        pass
    return None


def _spawn_hidden_cleanup(paths: list[Path]) -> None:
    """Hidden PowerShell helper: waits, then force-removes paths.

    No console window at all: powershell runs with -WindowStyle Hidden and the
    script is passed via -EncodedCommand (UTF-16LE base64), so Unicode paths
    and quoting are always safe.

    ВАЖНО: только CREATE_NO_WINDOW, БЕЗ DETACHED_PROCESS. Проверено live:
    Windows PowerShell 5.1 с флагом DETACHED_PROCESS стартует и сразу умирает,
    ничего не выполнив, — папки и удалятор остаются на месте.
    """
    if not paths:
        return
    items = ", ".join(
        "'" + str(p).replace("'", "''") + "'" for p in dict.fromkeys(paths)
    )
    script = (
        "$ErrorActionPreference='SilentlyContinue';"
        "Start-Sleep -Seconds 4;"
        f"$targets = @({items});"
        "foreach ($t in $targets) { "
        "  if (Test-Path -LiteralPath $t) { Remove-Item -LiteralPath $t -Recurse -Force }"
        "}"
    )
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    try:
        subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-WindowStyle",
                "Hidden",
                "-EncodedCommand",
                encoded,
            ],
            creationflags=subprocess.CREATE_NO_WINDOW,
            cwd=tempfile.gettempdir(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    except Exception:
        pass


class Banner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(170)
        self._image = QPixmap()
        try:
            folder = resource_root() / "panorama"
            images = [p for p in folder.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
            if images:
                chosen = random.choice(sorted(images, key=lambda p: p.name.lower()))
                loaded = QPixmap(str(chosen))
                if not loaded.isNull():
                    self._image = loaded
        except Exception:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self._image.isNull():
            painter.drawPixmap(rect, self._image)
            overlay = QLinearGradient(0, 0, 0, rect.height())
            overlay.setColorAt(0.0, QColor(5, 8, 18, 110))
            overlay.setColorAt(0.55, QColor(5, 8, 18, 40))
            overlay.setColorAt(1.0, QColor(5, 8, 18, 220))
            painter.fillRect(rect, overlay)
        else:
            gradient = QLinearGradient(0, 0, rect.width(), rect.height())
            gradient.setColorAt(0.0, QColor("#0B0E1A"))
            gradient.setColorAt(0.5, QColor("#1E1445"))
            gradient.setColorAt(1.0, QColor("#083044"))
            painter.fillRect(rect, gradient)

        mark = QPixmap(str(resource_root() / "assets" / "icons" / "LL.png"))
        if not mark.isNull():
            painter.drawPixmap(30, 45, 64, 64, mark)

        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.Black)
        font.setPixelSize(30)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(112, 86, "Удаление Lylos Launcher")

        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.DemiBold)
        font.setPixelSize(13)
        painter.setFont(font)
        painter.setPen(QColor("#C7D2FE"))
        painter.drawText(114, 114, "Полное удаление лаунчера и его данных")
        painter.end()


class UninstallerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Root")
        self.setWindowTitle("Удаление Lylos Launcher")
        self.setFixedSize(640, 460)
        self._running = False
        self._install_dir = resolve_install_dir() or APP_DIR

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(Banner())

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(14)

        warn = QLabel("Будут удалены:")
        warn.setObjectName("WarnTitle")

        lines = QLabel(
            f"• Папка установки и данных:\n   {self._install_dir}\n\n"
            "• Ярлыки в меню «Пуск» и на рабочем столе\n"
            "• Запись в «Настройки → Приложения» Windows\n\n"
            "Сборки, аккаунты, логи и скины будут удалены без возможности восстановления."
        )
        lines.setObjectName("Muted")
        lines.setWordWrap(True)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.close)
        self.uninstall_btn = QPushButton("Удалить Lylos Launcher")
        self.uninstall_btn.setObjectName("Danger")
        self.uninstall_btn.setFixedWidth(220)
        self.uninstall_btn.clicked.connect(self._start_uninstall)
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.uninstall_btn)

        layout.addWidget(warn)
        layout.addWidget(lines)
        layout.addWidget(self.progress)
        layout.addStretch(1)
        layout.addLayout(buttons)

        root.addWidget(body, 1)

    def _set_busy(self, busy: bool):
        self._running = busy
        self.uninstall_btn.setEnabled(not busy)
        self.cancel_btn.setEnabled(not busy)
        if busy:
            self.uninstall_btn.setText("Удаляю...")
            self.progress.show()

    def _start_uninstall(self):
        if self._running:
            return
        self._set_busy(True)
        self.progress.setValue(10)
        QTimer.singleShot(150, self._step_kill)

    # ------------------------------------------------------------- steps
    def _step_kill(self):
        for executable_name in ("LylosLauncher.exe", "SMLauncher.exe"):
            try:
                subprocess.run(
                    ["taskkill", "/f", "/im", executable_name],
                    capture_output=True,
                    timeout=10,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except Exception:
                pass
        self.progress.setValue(35)
        QTimer.singleShot(150, self._step_cleanup)

    def _step_cleanup(self):
        # Удаляем папку с ярлыком из общего меню «Пуск» всех пользователей
        # (C:\ProgramData\Microsoft\Windows\Start Menu\Programs\SMLauncher),
        # а также папку/ярлык в меню текущего пользователя и ярлык с рабочего стола.
        try:
            program_data = Path(os.environ.get("ProgramData") or Path("C:/ProgramData"))
            common_programs = program_data / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            for folder_name in (APP_NAME, LEGACY_APP_NAME):
                common_shortcuts = common_programs / folder_name
                if common_shortcuts.is_dir():
                    shutil.rmtree(common_shortcuts, ignore_errors=True)
        except Exception:
            pass
        try:
            appdata = os.environ.get("APPDATA")
            if appdata:
                user_programs = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
                for folder_name in (APP_NAME, LEGACY_APP_NAME):
                    user_shortcuts = user_programs / folder_name
                    if user_shortcuts.is_dir():
                        shutil.rmtree(user_shortcuts, ignore_errors=True)
                    (user_programs / f"{folder_name}.lnk").unlink(missing_ok=True)
        except Exception:
            pass
        try:
            desktop = Path.home() / "Desktop"
            for shortcut_name in (APP_NAME, LEGACY_APP_NAME):
                (desktop / f"{shortcut_name}.lnk").unlink(missing_ok=True)
        except Exception:
            pass
        # remove registry entries (Settings → Apps)
        _delete_registry_keys(UNINSTALL_REG_KEYS)
        self.progress.setValue(70)
        QTimer.singleShot(150, self._step_finalize)

    def _step_finalize(self):
        # 1) Отходим из папки установки — иначе Windows не даст её удалить,
        #    потому что текущая рабочая директория держится открытой.
        try:
            os.chdir(tempfile.gettempdir())
        except Exception:
            pass

        # 2) Собираем папки: реальная папка установки (из реестра) и папка
        #    данных %APPDATA%\\SMLauncher, если это другое место.
        install_dir = resolve_install_dir()
        folders: set[Path] = set()
        if install_dir is not None:
            folders.add(install_dir)
        for data_dir in (APP_DIR, LEGACY_APP_DIR):
            if _is_sm_folder(data_dir):
                folders.add(data_dir)

        # 3) Синхронно удаляем содержимое папок (кроме запущенного удалятора),
        #    показывая живой прогресс в UI.
        all_targets: list[Path] = []
        for folder in sorted(folders, key=str):
            all_targets.extend(_iter_delete_targets(folder))
        total = len(all_targets)
        for index, target in enumerate(all_targets, start=1):
            try:
                if target.is_dir() and not target.is_symlink():
                    shutil.rmtree(target, ignore_errors=True)
                else:
                    target.unlink(missing_ok=True)
            except Exception:
                pass
            pct = 72 + int(index / max(total, 1) * 18)
            self.progress.setValue(min(pct, 90))
            QApplication.processEvents()

        # 4) Скрытый помощник PowerShell (без консоли): ждёт, пока этот процесс
        #    завершится и EXE разблокируется, затем удаляет остатки папок
        #    и сам удалятор (файл запущенного EXE).
        targets: list[Path] = sorted(folders, key=str)
        self_exe = _running_uninstaller_exe()
        if self_exe is not None:
            targets.append(self_exe)
        _spawn_hidden_cleanup(targets)
        self.progress.setValue(95)
        QApplication.processEvents()

        self._set_busy(False)
        self.uninstall_btn.setEnabled(False)
        self.uninstall_btn.setText("Удалено ✓")
        self.progress.setValue(100)

        # Закрываем окно сразу — процесс завершится, EXE освободится,
        # и скрытый помощник без проблем доудалит папки и сам удалятор.
        QTimer.singleShot(250, self.close)


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    try:
        icon_path = resource_root() / "assets" / "LL.ico"
        if icon_path.exists():
            from PySide6.QtGui import QIcon
            app.setWindowIcon(QIcon(str(icon_path)))
    except Exception:
        pass

    window = UninstallerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())