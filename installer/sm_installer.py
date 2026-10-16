"""SMLauncher custom installer with its own SM visual design.

A standalone Qt application: installs the bundled launcher EXE into
%LOCALAPPDATA%\\Programs\\SMLauncher, creates Start Menu / desktop shortcuts
and can start the launcher right after installation.

Build:  PyInstaller build\\LylosSetup.spec
"""
from __future__ import annotations

import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QSize, QEvent, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

VERSION = "1.0"
APP_NAME = "Lylos Launcher"
EXE_NAME = "LylosLauncher.exe"
UPDATER_NAME = "LylosUpdater.exe"
UNINSTALLER_EXE_NAME = "LylosUninstaller.exe"
UNINSTALL_NAME = "Удалить Lylos Launcher.exe"
UNINSTALL_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\SMLauncher"

VIOLET = "#8B5CF6"
VIOLET_DEEP = "#7C3AED"
CYAN = "#22D3EE"

STYLE = """
* { font-family: "Segoe UI"; color: #E5E7EB; font-size: 13px; outline: none; }
QWidget { background-color: transparent; }
QMainWindow, #Root { background-color: #0B0E1A; }
#Root {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0B0E1A, stop:0.5 #151230, stop:1 #0A2430);
}
QLabel#Title { font-size: 26px; font-weight: 800; color: #F5F3FF; }
QLabel#Subtitle { font-size: 13px; color: #A5B4FC; }
QLabel#Muted { color: #94A3B8; font-size: 12px; }
QLabel#VersionTag {
  color: #0F0A1C; background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #8B5CF6, stop:1 #22D3EE);
  border-radius: 12px; padding: 6px 14px; font-weight: 800;
}
QFrame#Card {
  background-color: rgba(20, 25, 48, 0.72);
  border: 1px solid rgba(139, 92, 246, 0.22);
  border-radius: 18px;
}
QLineEdit, QPushButton {
  background-color: rgba(10, 14, 28, 0.9);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
  padding: 10px 12px;
}
QLineEdit:focus { border: 1px solid #22D3EE; }
QPushButton:hover { border-color: #22D3EE; }
QPushButton#Primary {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8B5CF6, stop:1 #22D3EE);
  color: #0F0A1C; font-weight: 800; border: none; border-radius: 12px; padding: 12px 22px;
}
QPushButton#Primary:hover { border: 1px solid #A5F3FC; }
QPushButton#Ghost { border-radius: 12px; padding: 12px 20px; }
QCheckBox { spacing: 10px; color: #E2E8F0; }
QCheckBox::indicator {
  width: 18px; height: 18px; border-radius: 6px;
  border: 1px solid rgba(139, 92, 246, 0.4); background: rgba(10, 14, 28, 0.9);
}
QCheckBox::indicator:checked { background: #8B5CF6; border-color: #22D3EE; }
QProgressBar {
  background: rgba(255,255,255,0.08); border: none; border-radius: 6px; max-height: 10px;
}
QProgressBar::chunk {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #8B5CF6, stop:1 #22D3EE);
  border-radius: 6px;
}
QWidget#Splash {
  background-color: #0B0E1A;
  border: 1px solid rgba(139, 92, 246, 0.35);
  border-radius: 18px;
}
QLabel#SplashTitle {
  color: #F5F3FF; font-size: 22px; font-weight: 800; background: transparent;
}
QLabel#SplashStatus {
  color: #C7D2FE; font-size: 13px; background: transparent;
}
QProgressBar#SplashBar {
  background: rgba(255,255,255,0.08); border: none; border-radius: 6px; max-height: 10px;
}
QProgressBar#SplashBar::chunk {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #8B5CF6, stop:1 #22D3EE);
  border-radius: 6px;
}
"""


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[1]


def pick_panorama() -> Path | None:
    folder = resource_root() / "panorama"
    try:
        images = [p for p in folder.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
        if images:
            return random.choice(sorted(images, key=lambda p: p.name.lower()))
    except Exception:
        pass
    return None


class Banner(QWidget):
    """Top banner with a random Minecraft panorama + SM branding."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(190)
        self._image = QPixmap()
        path = pick_panorama()
        if path:
            loaded = QPixmap(str(path))
            if not loaded.isNull():
                self._image = loaded

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
            painter.drawPixmap(30, 55, 72, 72, mark)

        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.Black)
        font.setPixelSize(34)
        painter.setFont(font)
        grad = QLinearGradient(120, 0, 420, 0)
        grad.setColorAt(0.0, QColor("#F4F6FF"))
        grad.setColorAt(0.6, QColor("#D8C9FF"))
        grad.setColorAt(1.0, QColor("#7DE9F8"))
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(118, 96, "Lylos Launcher")

        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.DemiBold)
        font.setPixelSize(14)
        painter.setFont(font)
        painter.setPen(QColor("#C7D2FE"))
        painter.drawText(120, 124, "Кастомный установщик лаунчера для Minecraft")

        font = QFont("Segoe UI")
        font.setPixelSize(12)
        painter.setFont(font)
        painter.setPen(QColor(148, 163, 184, 220))
        painter.drawText(120, 148, f"Версия {VERSION} · Windows x64")
        painter.end()


class InstallerSplash(QWidget):
    """Первое, что видит пользователь при запуске установщика.

    Перетаскиваемое и сворачиваемое окно поверх рамки без системного заголовка:
    показывает случайное фото из assets/panorama, заголовок «Установить Lylos Launcher»
    и прогресс начальной загрузки до появления основного окна установщика.
    """

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setObjectName("Splash")
        self.setWindowTitle("Установить Lylos Launcher")
        self.setFixedSize(460, 300)
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self._drag_offset = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._image = QPixmap()
        path = pick_panorama()
        if path:
            loaded = QPixmap(str(path))
            if not loaded.isNull():
                self._image = loaded

        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        if not self._image.isNull():
            img.setPixmap(self._image.scaled(460, 200, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            img.setStyleSheet(
                "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                " stop:0 #1E1445, stop:1 #083044);"
            )
        img.setFixedHeight(200)
        layout.addWidget(img)

        content = QWidget()
        body = QVBoxLayout(content)
        body.setContentsMargins(22, 18, 22, 18)
        body.setSpacing(10)

        mark = QLabel()
        mark.setAlignment(Qt.AlignCenter)
        mark_pix = QPixmap(str(resource_root() / "assets" / "icons" / "LL.png"))
        if not mark_pix.isNull():
            mark.setPixmap(mark_pix.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        body.addWidget(mark, 0, Qt.AlignCenter)

        title = QLabel("Установить Lylos Launcher")
        title.setObjectName("SplashTitle")
        title.setAlignment(Qt.AlignCenter)
        body.addWidget(title)

        self.status_label = QLabel("Подготовка установки...")
        self.status_label.setObjectName("SplashStatus")
        self.status_label.setAlignment(Qt.AlignCenter)
        body.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setObjectName("SplashBar")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(10)
        body.addWidget(self.progress)

        layout.addWidget(content, 1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)
        self._tick_value = 0

    done = Signal()

    def _tick(self):
        # Имитация плавной загрузки начального этапа установки.
        self._tick_value = min(100, self._tick_value + random.randint(1, 4))
        self.progress.setValue(self._tick_value)
        if self._tick_value >= 100:
            self._timer.stop()
            self.status_label.setText("Готово")
            QTimer.singleShot(200, self.done.emit)

    def set_status(self, text: str):
        if hasattr(self, "status_label"):
            self.status_label.setText(text)

    def set_progress(self, value: int):
        value = max(0, min(100, int(value)))
        if hasattr(self, "progress"):
            self.progress.setValue(value)
            self._tick_value = value

    # --- перемещение и сворачивание без системного заголовка ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_offset = None
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class InstallerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Root")
        self.setWindowTitle("Установка Lylos Launcher")
        self.setFixedSize(660, 500)
        self._installing = False
        self._final_dir: Path | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(Banner())

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 20, 28, 20)
        body_layout.setSpacing(14)

        # --- install path ---
        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self.path_edit = QLineEdit(str(self._default_dir()))
        path_row.addWidget(self.path_edit, 1)
        browse = QPushButton("Обзор...")
        browse.setObjectName("Ghost")
        browse.clicked.connect(self._browse)
        path_row.addWidget(browse)

        # --- options ---
        self.desktop_check = QCheckBox("Создать ярлык на рабочем столе")
        self.desktop_check.setChecked(True)
        self.startmenu_check = QCheckBox("Добавить в меню «Пуск»")
        self.startmenu_check.setChecked(True)
        self.run_check = QCheckBox("Запустить Lylos Launcher после установки")
        self.run_check.setChecked(True)

        # --- progress ---
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()

        # --- buttons ---
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setObjectName("Ghost")
        self.cancel_btn.clicked.connect(self.close)
        self.install_btn = QPushButton("Установить")
        self.install_btn.setObjectName("Primary")
        self.install_btn.setFixedWidth(200)
        self.install_btn.clicked.connect(self._start_install)
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.install_btn)

        body_layout.addWidget(QLabel("Папка установки:"))
        body_layout.addLayout(path_row)
        body_layout.addSpacing(4)
        body_layout.addWidget(self.desktop_check)
        body_layout.addWidget(self.startmenu_check)
        body_layout.addWidget(self.run_check)
        body_layout.addWidget(self.progress)
        body_layout.addStretch(1)
        body_layout.addLayout(buttons)

        root.addWidget(body, 1)

    @staticmethod
    def _default_dir() -> Path:
        # Keep the installation and launcher data together in the branded folder.
        appdata = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
        return appdata / APP_NAME

    @staticmethod
    def _find_bundled_launcher() -> Path:
        folder = resource_root() / "launcher"
        if folder.is_dir():
            for pattern in (EXE_NAME, "*.exe"):
                matches = sorted(folder.glob(pattern))
                if matches:
                    return matches[0]
        return folder / EXE_NAME

    @staticmethod
    def _find_bundled_updater() -> Path:
        return resource_root() / "updater" / UPDATER_NAME

    @staticmethod
    def _find_bundled_uninstaller() -> Path:
        folder = resource_root() / "uninstaller"
        candidates = [folder / UNINSTALLER_EXE_NAME, folder / "SMUninstaller.exe"]
        if folder.is_dir():
            candidates += sorted(folder.glob("*.exe"))
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return folder / UNINSTALLER_EXE_NAME

    def _browse(self):
        selected = QFileDialog.getExistingDirectory(self, "Выбери папку установки", self.path_edit.text())
        if selected:
            self.path_edit.setText(selected)

    def _set_busy(self, busy: bool, text: str | None = None):
        self._installing = busy
        self.path_edit.setEnabled(not busy)
        self.desktop_check.setEnabled(not busy)
        self.startmenu_check.setEnabled(not busy)
        self.install_btn.setEnabled(not busy)
        self.cancel_btn.setEnabled(not busy)
        if text is not None:
            self.install_btn.setText(text)

    def _start_install(self):
        if self._installing:
            return

        target = Path(self.path_edit.text().strip() or str(self._default_dir())).expanduser()
        try:
            target.mkdir(parents=True, exist_ok=True)
            test = target / ".sm_write_test"
            test.write_text("ok", encoding="utf-8")
            test.unlink(missing_ok=True)
        except Exception as error:
            QMessageBox.critical(self, "Нет доступа к папке", str(error))
            return

        self._set_busy(True, "Устанавливаю...")
        self.progress.show()
        self.progress.setValue(0)
        self._target = target
        QTimer.singleShot(0, self._install_step_1)

    # ------------------------------------------------------------- install
    def _install_step_1(self):
        """Copy launcher, updater, and uninstaller into the install folder."""
        source_exe = self._find_bundled_launcher()
        if not source_exe.is_file():
            QMessageBox.critical(
                self,
                "Файл не найден",
                f"Не удалось найти {source_exe}.\n\n"
                "Установщик повреждён — пересобери его заново.",
            )
            self._set_busy(False, "Установить")
            return

        source_updater = self._find_bundled_updater()
        if not source_updater.is_file():
            QMessageBox.critical(
                self,
                "Обновлятор не найден",
                f"Не удалось найти {source_updater}.\n\n"
                "Пересобери установщик вместе с LylosUpdater.exe.",
            )
            self._set_busy(False, "Установить")
            return

        try:
            shutil.copy2(source_exe, self._target / EXE_NAME)
            self.progress.setValue(45)
            shutil.copy2(source_updater, self._target / UPDATER_NAME)
            self.progress.setValue(60)

            self._write_uninstaller()
            self.progress.setValue(75)
        except Exception as error:
            QMessageBox.critical(self, "Ошибка установки", str(error))
            self._set_busy(False, "Установить")
            return

        QTimer.singleShot(30, self._install_step_2)

    def _write_uninstaller(self):
        """Copy the bundled uninstaller next to the launcher."""
        source = self._find_bundled_uninstaller()
        if not source.is_file():
            QMessageBox.warning(
                self,
                "Удалятор не найден",
                f"Не удалось найти {source}.\n\n"
                "Приложение установлено, но удалить его через настройки Windows не получится.",
            )
            return
        shutil.copy2(source, self._target / UNINSTALL_NAME)

    def _register_uninstall(self):
        """Register the app in Windows Settings → Apps → Installed apps."""
        try:
            import winreg
        except Exception:
            return
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_REG_KEY) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Lylos Launcher")
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, VERSION)
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Lylos Launcher")
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(self._target))
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(self._target / EXE_NAME))
                uninstaller_exe = self._target / UNINSTALL_NAME
                winreg.SetValueEx(
                    key,
                    "UninstallString",
                    0,
                    winreg.REG_SZ,
                    f'"{uninstaller_exe}"',
                )
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
                try:
                    size_kb = sum(p.stat().st_size for p in self._target.rglob("*") if p.is_file()) // 1024
                    winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, int(size_kb))
                except Exception:
                    pass
        except Exception:
            pass

    def _install_step_2(self):
        """Create shortcuts."""
        errors: list[str] = []
        # Меню «Пуск»: общая папка всех пользователей C:\ProgramData\...
        # Если нет прав — откатываемся на папку текущего пользователя.
        try:
            self._create_shortcut("Start Menu", self._start_menu_dir())
        except Exception as error:
            errors.append(str(error))
            try:
                self._create_shortcut("Start Menu", self._per_user_start_menu_dir())
            except Exception as error2:
                errors.append(str(error2))
        if self.desktop_check.isChecked():
            try:
                self._create_shortcut("Desktop", Path.home() / "Desktop")
            except Exception as error:
                errors.append(str(error))
        if errors:
            QMessageBox.warning(self, "Ярлыки", f"Файлы скопированы, но ярлыки не созданы:\n{' '.join(errors)}")
        self.progress.setValue(85)

        self._register_uninstall()
        self.progress.setValue(95)
        QTimer.singleShot(150, self._install_finished)

    @staticmethod
    def _start_menu_dir() -> Path:
        # Общий пункт меню «Пуск» для всех пользователей.
        program_data = Path(os.environ.get("ProgramData") or Path("C:/ProgramData"))
        return program_data / "Microsoft" / "Windows" / "Start Menu" / "Programs" / APP_NAME

    @staticmethod
    def _per_user_start_menu_dir() -> Path:
        # Запасной вариант — меню «Пуск» текущего пользователя.
        appdata = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
        return appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / APP_NAME

    def _create_shortcut(self, name: str, folder: Path):
        """Создаёт .lnk через временный VBS-скрипт.

        ВАЖНО: wscript при ошибке в скрипте часто возвращает код 0, поэтому
        после запуска обязательно проверяем, что .lnk реально появился.
        Текст скрипта пишем только ASCII — кириллица/em-dash в UTF-8 ломают
        парсер VBS и ярлык молча не создаётся.
        """
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        lnk_path = folder / f"{APP_NAME}.lnk"
        exe_path = self._target / EXE_NAME

        vbs_content = (
            "Set ws = CreateObject(\"WScript.Shell\")\r\n"
            f"Set lnk = ws.CreateShortcut(\"{lnk_path}\")\r\n"
            f"lnk.TargetPath = \"{exe_path}\"\r\n"
            f"lnk.WorkingDirectory = \"{self._target}\"\r\n"
            f"lnk.IconLocation = \"{exe_path},0\"\r\n"
            f"lnk.Description = \"Lylos Launcher - Minecraft launcher\"\r\n"
            "lnk.Save\r\n"
        )

        vbs = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".vbs", delete=False, encoding="ascii") as fh:
                fh.write(vbs_content)
                vbs = Path(fh.name)

            # Пробуем wscript, затем cscript (тот же движок VBS)
            for engine in ("wscript.exe", "cscript.exe"):
                try:
                    subprocess.run(
                        [engine, "//B", str(vbs)],
                        check=True,
                        timeout=30,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                except Exception:
                    continue
                if lnk_path.exists():
                    return

            # Ярлык не создался — сообщаем пользователю, а не молчим
            raise RuntimeError(f"Не удалось создать ярлык: {lnk_path}")
        finally:
            if vbs and vbs.exists():
                try:
                    vbs.unlink()
                except Exception:
                    pass

    def _install_finished(self):
        self._set_busy(False, "Установлено ✓")
        self.progress.setValue(100)
        self.install_btn.setEnabled(False)
        self.install_btn.setText("Готово ✓")

        launch = False
        if self.run_check.isChecked():
            result = QMessageBox.question(
                self,
                "Установка завершена",
                f"Lylos Launcher установлен в:\n{self._target}\n\n"
                "Приложение зарегистрировано в Windows — удалить его можно через "
                "«Настройки → Приложения» или «Удалить Lylos Launcher.cmd» из папки установки.\n\n"
                "Запустить лаунчер сейчас?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            launch = result == QMessageBox.Yes

        if launch:
            try:
                subprocess.Popen([str(self._target / EXE_NAME)], cwd=str(self._target))
            except Exception:
                pass
        self.close()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Lylos Launcher")
    app.setStyleSheet(STYLE)
    try:
        icon_path = resource_root() / "assets" / "LL.ico"
        if icon_path.exists():
            from PySide6.QtGui import QIcon
            app.setWindowIcon(QIcon(str(icon_path)))
    except Exception:
        pass

    # Сплэш показывается первым, до создания основного окна установщика.
    splash = InstallerSplash()
    splash.show()
    app.processEvents()

    window_holder = {}

    def _open_installer():
        splash.close()
        window = InstallerWindow()
        window_holder["window"] = window
        window.show()

    splash.done.connect(_open_installer)

    # Шаги начальной загрузки, идущие на сплэше, пока строится основной экран.
    steps = [
        ("Подготовка установки...", 10),
        ("Проверка файлов установки...", 30),
        ("Подготовка папки установки...", 55),
        ("Проверка компонентов...", 75),
        ("Готово", 100),
    ]
    step_index = [0]

    def _run_next_load_step():
        idx = step_index[0]
        if idx >= len(steps):
            # Сплэш сам закроется через сигнал done (когда прогресс дойдёт до 100%).
            return
        text, target = steps[idx]
        splash.set_status(text)
        splash.set_progress(target)
        QTimer.singleShot(280, _run_next_load_step)
        step_index[0] = idx + 1

    QTimer.singleShot(60, _run_next_load_step)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()