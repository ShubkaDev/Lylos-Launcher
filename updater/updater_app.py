"""Lylos Launcher Updater — визуальная часть (логика подключается позже).

Отдельное приложение, которое в будущем будет скачивать и устанавливать
новые версии Lylos Launcher. Сейчас — только интерфейс: красивое окно с
логотипом, статусом, прогресс-баром и кнопками.

Сборка в EXE:  pyinstaller --noconfirm build\\LylosUpdater.spec
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlparse, urlsplit, urlunsplit

from PySide6.QtCore import QRectF, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

VIOLET = "#8B5CF6"
VIOLET_DEEP = "#7C3AED"
CYAN = "#22D3EE"

WINDOW_W = 760
WINDOW_H = 540

_STYLE = """
QWidget#UpdaterRoot { background-color: #02040C; }
QLabel#UpdaterTitle {
    color: #F4F6FF;
    font-size: 40px;
    font-weight: 900;
    letter-spacing: 4px;
}
QLabel#UpdaterSubtitle {
    color: #94A3B8;
    font-size: 14px;
}
QFrame#UpdaterCard {
    background-color: rgba(6, 11, 24, 0.96);
    border: 2px solid rgba(34, 211, 238, 0.45);
    border-radius: 20px;
}
QLabel#UpdaterStatus {
    color: #E2E8F0;
    font-size: 15px;
    font-weight: 700;
}
QLabel#UpdaterDetail {
    color: #94A3B8;
    font-size: 13px;
}
QProgressBar#UpdaterProgress {
    background-color: rgba(10, 17, 32, 0.9);
    border: none;
    border-radius: 6px;
    min-height: 14px;
    max-height: 14px;
    text-visible: false;
}
QProgressBar#UpdaterProgress::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B5CF6, stop:1 #22D3EE);
    border-radius: 6px;
}
QPushButton#UpdaterPrimaryButton {
    background-color: rgba(124, 58, 237, 0.55);
    border: 2px solid #22D3EE;
    border-radius: 16px;
    color: #FFFFFF;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 800;
}
QPushButton#UpdaterPrimaryButton:hover {
    background-color: rgba(124, 58, 237, 0.85);
    border-color: #67E8F9;
}
QPushButton#UpdaterPrimaryButton:disabled {
    background-color: rgba(124, 58, 237, 0.25);
    border-color: rgba(34, 211, 238, 0.30);
    color: #94A3B8;
}
QPushButton#UpdaterGhostButton {
    background-color: rgba(6, 11, 24, 0.96);
    border: 1px solid rgba(148, 163, 184, 0.45);
    border-radius: 14px;
    color: #E2E8F0;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 700;
}
QPushButton#UpdaterGhostButton:hover {
    background-color: rgba(124, 58, 237, 0.30);
    border-color: rgba(34, 211, 238, 0.70);
}
"""


class UpdaterBackground(QWidget):
    """Фон с градиентом и логотипом LL."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UpdaterRoot")
        self.setAttribute(Qt.WA_StyledBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        gradient.setColorAt(0.0, QColor("#0B0E1A"))
        gradient.setColorAt(0.5, QColor("#1E1445"))
        gradient.setColorAt(1.0, QColor("#083044"))
        painter.fillRect(rect, gradient)

        # Логотип LL в центре сверху.
        mark_size = 72
        mark_rect = QRectF(rect.width() / 2 - mark_size / 2, 46, mark_size, mark_size)
        mark_grad = QLinearGradient(mark_rect.topLeft(), mark_rect.bottomRight())
        mark_grad.setColorAt(0.0, QColor(VIOLET))
        mark_grad.setColorAt(0.55, QColor(VIOLET_DEEP))
        mark_grad.setColorAt(1.0, QColor(CYAN))
        painter.setBrush(mark_grad)
        painter.setPen(QPen(QColor(255, 255, 255, 90), 1.5))
        painter.drawRoundedRect(mark_rect, 20, 20)
        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.Black)
        font.setPixelSize(30)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(mark_rect, Qt.AlignmentFlag.AlignCenter, "LL")

        painter.end()


def _encode_url(url: str) -> str:
    """Percent-encode non-ASCII characters in URL path/query.

    urllib/http.client отправляет строку запроса в ASCII и падает с
    ``UnicodeEncodeError`` на кириллице (например, тег релиза «Релизы»).
    Кодируем путь и query, сохраняя уже закодированные ``%XX``.
    """
    parts = urlsplit(str(url or ""))
    path = quote(parts.path, safe="/%:@!$&'()*+,;=-._~")
    query = quote(parts.query, safe="=&%:@!$'()*+,;/?-._~")
    return urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


class UpdateWorker(QThread):
    progress_changed = Signal(int)
    status_changed = Signal(str, str)
    update_succeeded = Signal(str)
    update_failed = Signal(str)

    release_json_url = "https://shubkadev.github.io/Lylos-Launcher/release.json"

    def __init__(self, install_dir: Path, wait_pid: int | None = None):
        super().__init__()
        self.install_dir = install_dir.resolve()
        self.update_dir = self.install_dir / "update"
        self.wait_pid = wait_pid

    def run(self):
        try:
            if self.wait_pid:
                self.status_changed.emit("Ожидание закрытия лаунчера...", "Сохраняем файлы перед заменой.")
                self._wait_for_process(self.wait_pid)
            self.update_dir.mkdir(parents=True, exist_ok=True)
            self.status_changed.emit("Получение обновления...", "Читаем ссылку из release.json.")
            release = self._fetch_release()
            archive_path = self.update_dir / "update.zip"
            self._download_archive(release["download_url"], archive_path)
            payload_dir = self.update_dir / "payload"
            if payload_dir.exists():
                shutil.rmtree(payload_dir)
            payload_dir.mkdir(parents=True)
            self.status_changed.emit("Проверка архива...", "Безопасно распаковываем файлы обновления.")
            self._extract_archive(archive_path, payload_dir)
            launcher_names = ("LylosLauncher.exe", "SMLauncher.exe")
            if not any((payload_dir / name).is_file() for name in launcher_names):
                raise RuntimeError("В архиве не найден LylosLauncher.exe или совместимый SMLauncher.exe.")
            self._install_payload(payload_dir)
            self.progress_changed.emit(96)
            subprocess.Popen([str(self.install_dir / "LylosLauncher.exe")], cwd=str(self.install_dir))
            self._schedule_cleanup()
            self.update_succeeded.emit(release["version"])
        except Exception as error:
            self.update_failed.emit(str(error))

    @staticmethod
    def _wait_for_process(process_id: int):
        if os.name == "nt":
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            handle = kernel32.OpenProcess(0x00100000, False, process_id)
            if handle:
                try:
                    kernel32.WaitForSingleObject(handle, 0xFFFFFFFF)
                finally:
                    kernel32.CloseHandle(handle)
            return
        while True:
            try:
                os.kill(process_id, 0)
            except OSError:
                return
            QThread.msleep(250)

    def _fetch_release(self) -> dict[str, str]:
        request = urllib.request.Request(
            _encode_url(self.release_json_url),
            headers={"User-Agent": "LylosLauncher-Updater/1.0"},
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            raw_data = response.read(65537)
        if len(raw_data) > 65536:
            raise RuntimeError("release.json слишком большой.")
        payload = json.loads(raw_data.decode("utf-8"))
        version = payload.get("version")
        download_url = payload.get("download_url")
        parsed_url = urlparse(download_url or "")
        if not isinstance(version, str) or not version.strip():
            raise RuntimeError("В release.json отсутствует версия обновления.")
        if parsed_url.scheme != "https" or not parsed_url.path.lower().endswith(".zip"):
            raise RuntimeError("В release.json указана некорректная HTTPS-ссылка на ZIP.")
        return {"version": version.strip(), "download_url": download_url}

    def _download_archive(self, download_url: str, archive_path: Path):
        self.status_changed.emit("Скачивание обновления...", "Загружаем ZIP-архив.")
        request = urllib.request.Request(_encode_url(download_url), headers={"User-Agent": "LylosLauncher-Updater/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response, archive_path.open("wb") as archive:
            total = int(response.headers.get("Content-Length", "0") or 0)
            received = 0
            while chunk := response.read(1024 * 256):
                archive.write(chunk)
                received += len(chunk)
                if total:
                    self.progress_changed.emit(min(75, int(received * 75 / total)))
        if not zipfile.is_zipfile(archive_path):
            raise RuntimeError("Сервер вернул файл, который не является ZIP-архивом.")

    def _extract_archive(self, archive_path: Path, payload_dir: Path):
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            for index, entry in enumerate(entries, start=1):
                normalized = entry.filename.replace("\\", "/")
                if normalized.startswith("/"):
                    raise RuntimeError("В архиве обнаружен недопустимый абсолютный путь.")
                parts = list(PurePosixPath(normalized).parts)
                if parts and parts[0].lower() == "smlauncher":
                    parts = parts[1:]
                if not parts or any(part in (".", "..") or ":" in part for part in parts):
                    raise RuntimeError("В архиве обнаружен небезопасный путь.")
                if parts[0].lower() in {"data", "update"}:
                    continue
                mode = entry.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise RuntimeError("В архиве обнаружена символическая ссылка.")
                destination = payload_dir.joinpath(*parts)
                if not destination.resolve().is_relative_to(payload_dir.resolve()):
                    raise RuntimeError("Путь архива выходит за пределы папки распаковки.")
                if entry.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(entry) as source, destination.open("wb") as target:
                        shutil.copyfileobj(source, target)
                self.progress_changed.emit(75 + int(index * 15 / max(len(entries), 1)))

    def _install_payload(self, payload_dir: Path):
        self.status_changed.emit("Установка файлов...", "Заменяем программу, не затрагивая папку data.")
        has_branded_launcher = (payload_dir / "LylosLauncher.exe").is_file()
        for source in payload_dir.rglob("*"):
            relative = source.relative_to(payload_dir)
            if relative.parts[0].lower() in {"data", "update"}:
                continue
            if source.name.lower() == "smlauncher.exe":
                if has_branded_launcher:
                    continue
                relative = relative.with_name("LylosLauncher.exe")
            destination = self.install_dir / relative
            if source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        for old_name in ("SMLauncher.exe", "SMUninstaller.exe", "Удалить SMLauncher.exe"):
            (self.install_dir / old_name).unlink(missing_ok=True)

    def _schedule_cleanup(self):
        update_path = str(self.update_dir.resolve()).replace("'", "''")
        command = (
            f"$target='{update_path}'; $processId={os.getpid()}; "
            "while (Get-Process -Id $processId -ErrorAction SilentlyContinue) { Start-Sleep -Milliseconds 500 }; "
            "Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction SilentlyContinue"
        )
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
        subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden", "-Command", command],
            cwd=str(self.install_dir),
            creationflags=flags,
            close_fds=True,
        )


class UpdaterWindow(QMainWindow):
    """Окно обновления Lylos Launcher."""

    def __init__(self, install_dir: Path, wait_pid: int | None = None):
        super().__init__()
        self.setWindowTitle("Lylos Launcher — Обновление")
        self.setFixedSize(WINDOW_W, WINDOW_H)
        self.install_dir = install_dir
        self.wait_pid = wait_pid
        self.worker: UpdateWorker | None = None

        try:
            icon_path = PROJECT_ROOT / "assets" / "LL.ico"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass

        self._build_ui()

    def _build_ui(self):
        root = UpdaterBackground()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(40, 150, 40, 40)
        layout.setSpacing(14)

        title = QLabel("Lylos Launcher")
        title.setObjectName("UpdaterTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Обновление лаунчера")
        subtitle.setObjectName("UpdaterSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addStretch(1)

        # --- карточка статуса ---
        card = QFrame()
        card.setObjectName("UpdaterCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)

        self.status_label = QLabel("Готов к проверке обновлений")
        self.status_label.setObjectName("UpdaterStatus")
        card_layout.addWidget(self.status_label)

        self.detail_label = QLabel("Нажмите «Проверить обновления», чтобы узнать о новой версии.")
        self.detail_label.setObjectName("UpdaterDetail")
        self.detail_label.setWordWrap(True)
        card_layout.addWidget(self.detail_label)

        self.progress = QProgressBar()
        self.progress.setObjectName("UpdaterProgress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        card_layout.addWidget(self.progress)

        layout.addWidget(card, 1)

        # --- кнопки ---
        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        self.check_btn = QPushButton("Начать обновление")
        self.check_btn.setObjectName("UpdaterPrimaryButton")
        self.check_btn.setCursor(Qt.PointingHandCursor)
        self.check_btn.clicked.connect(self._on_check_clicked)
        buttons.addWidget(self.check_btn)

        self.install_btn = QPushButton("Установить обновление")
        self.install_btn.setObjectName("UpdaterPrimaryButton")
        self.install_btn.setVisible(False)

        buttons.addStretch(1)

        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("UpdaterGhostButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)

        layout.addLayout(buttons)

    # ------------------------------------------------------------- actions
    def start_update(self):
        if self.worker is not None and self.worker.isRunning():
            return
        self.check_btn.setEnabled(False)
        self.install_btn.setEnabled(False)
        self.progress.setValue(0)
        self.status_label.setText("Запуск обновления...")
        self.detail_label.setText("Подготавливаем загрузку файлов лаунчера.")
        self.worker = UpdateWorker(self.install_dir, self.wait_pid)
        self.worker.progress_changed.connect(self.progress.setValue)
        self.worker.status_changed.connect(self._on_status_changed)
        self.worker.update_succeeded.connect(self._on_update_succeeded)
        self.worker.update_failed.connect(self._on_update_failed)
        self.worker.start()

    def _on_check_clicked(self):
        self.start_update()

    def _on_status_changed(self, title: str, detail: str):
        self.status_label.setText(title)
        self.detail_label.setText(detail)

    def _on_update_succeeded(self, version: str):
        self.progress.setValue(100)
        self.status_label.setText(f"Установлена версия {version}")
        self.detail_label.setText("Запускаем обновлённый лаунчер.")
        QTimer.singleShot(700, self.close)

    def _on_update_failed(self, error: str):
        self.status_label.setText("Не удалось установить обновление")
        self.detail_label.setText(error)
        self.check_btn.setEnabled(True)


def main():
    parser = argparse.ArgumentParser(description="Обновление Lylos Launcher")
    parser.add_argument("--install-dir", type=Path)
    parser.add_argument("--wait-pid", type=int)
    arguments = parser.parse_args()

    executable_dir = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
    default_install_dir = executable_dir.parent if executable_dir.name.lower() == "update" else executable_dir
    install_dir = (arguments.install_dir or default_install_dir).resolve()

    app = QApplication(sys.argv)
    app.setApplicationName("Lylos Launcher Updater")
    app.setStyleSheet(_STYLE)
    window = UpdaterWindow(install_dir, arguments.wait_pid)
    window.show()
    if arguments.wait_pid is not None:
        QTimer.singleShot(0, window.start_update)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()