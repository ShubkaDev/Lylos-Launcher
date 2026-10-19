"""Отдельное окно управления Java: что скачано и загрузка новых сред."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.java_downloader import find_managed_java, list_managed_java

DOWNLOAD_MAJORS = (8, 11, 17, 21)


class JavaDownloadWorker(QThread):
    progress = Signal(int, int)  # major, percent
    done = Signal(int, str)
    failed = Signal(int, str)

    def __init__(self, major: int, parent=None):
        super().__init__(parent)
        self.major = major

    def run(self):
        try:
            from core.java_downloader import download_managed_java

            def on_progress(downloaded, total):
                percent = int(downloaded * 100 / total) if total else 0
                self.progress.emit(self.major, max(0, min(100, percent)))

            path = download_managed_java(self.major, progress_callback=on_progress)
            self.done.emit(self.major, str(path))
        except Exception as error:
            self.failed.emit(self.major, str(error))


class JavaManagerWindow(QDialog):
    """Список скачанных Java и загрузка новых прямо из окна."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Java — Lylos Launcher")
        self.setMinimumSize(640, 480)
        self.setModal(False)
        self._workers: dict[int, JavaDownloadWorker] = {}
        self._rows: dict[int, dict] = {}

        try:
            icon_path = Path(__file__).resolve().parents[2] / "assets" / "LL.ico"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass

        self._build()
        self.refresh()

    # ---------------------------------------------------------------- UI
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(14)

        title = QLabel("Java")
        title.setObjectName("PageTitle")
        subtitle = QLabel(
            "Здесь видно, какие Java уже скачаны, и можно скачать нужную версию — "
            "лаунчер подхватит её автоматически."
        )
        subtitle.setObjectName("MutedText")
        subtitle.setWordWrap(True)

        root.addWidget(title)
        root.addWidget(subtitle)

        installed = QFrame()
        installed.setObjectName("Card")
        installed_layout = QVBoxLayout(installed)
        installed_layout.setContentsMargins(18, 16, 18, 16)
        installed_layout.setSpacing(8)

        installed_title = QLabel("Скачанные Java")
        installed_title.setObjectName("SectionTitle")
        installed_layout.addWidget(installed_title)

        self.installed_container = QWidget()
        self.installed_layout = QVBoxLayout(self.installed_container)
        self.installed_layout.setContentsMargins(0, 0, 0, 0)
        self.installed_layout.setSpacing(6)
        installed_layout.addWidget(self.installed_container)

        root.addWidget(installed)

        download_box = QFrame()
        download_box.setObjectName("Card")
        download_layout = QVBoxLayout(download_box)
        download_layout.setContentsMargins(18, 16, 18, 16)
        download_layout.setSpacing(10)

        download_title = QLabel("Скачать Java")
        download_title.setObjectName("SectionTitle")
        download_layout.addWidget(download_title)

        for major in DOWNLOAD_MAJORS:
            download_layout.addWidget(self._make_row(major))

        root.addWidget(download_box, 1)

        close_row = QHBoxLayout()
        close_row.addStretch(1)
        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("SecondaryButton")
        close_btn.clicked.connect(self.close)
        close_row.addWidget(close_btn)
        root.addLayout(close_row)

    def _make_row(self, major: int) -> QWidget:
        row = QFrame()
        row.setObjectName("MiniCard")
        layout = QVBoxLayout(row)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        top = QHBoxLayout()
        name = QLabel(f"Java {major}")
        name.setObjectName("CardTitle")
        status = QLabel("Проверка…")
        status.setObjectName("MutedText")

        button = QPushButton("Скачать")
        button.setObjectName("SecondaryButton")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda checked=False, m=major: self._download(m))

        top.addWidget(name)
        top.addWidget(status, 1)
        top.addWidget(button)

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.hide()

        layout.addLayout(top)
        layout.addWidget(progress)

        self._rows[major] = {
            "status": status,
            "button": button,
            "progress": progress,
        }
        return row

    # ------------------------------------------------------------ data
    def refresh(self):
        installed = list_managed_java()
        installed_majors = {item["major"] for item in installed if item.get("installed")}

        # Перерисовать список установленных.
        while self.installed_layout.count():
            item = self.installed_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not installed_majors:
            empty = QLabel("Пока ничего не скачано.")
            empty.setObjectName("MutedText")
            self.installed_layout.addWidget(empty)
        else:
            for major in sorted(installed_majors):
                java_exe = find_managed_java(major)
                line = QLabel(f"• Java {major} — {java_exe}")
                line.setObjectName("MutedText")
                line.setWordWrap(True)
                line.setTextInteractionFlags(Qt.TextSelectableByMouse)
                self.installed_layout.addWidget(line)

        # Обновить статусы строк загрузки.
        for major, row in self._rows.items():
            if major in installed_majors:
                row["status"].setText("установлена")
                row["button"].setText("Переустановить")
                row["button"].setEnabled(True)
            else:
                row["status"].setText("не скачана")
                row["button"].setText("Скачать")
                row["button"].setEnabled(True)

    # -------------------------------------------------------- download
    def _download(self, major: int):
        worker = self._workers.get(major)
        if worker is not None and worker.isRunning():
            return

        row = self._rows[major]
        row["button"].setEnabled(False)
        row["button"].setText("Загрузка…")
        row["progress"].setValue(0)
        row["progress"].show()
        row["status"].setText("скачивание…")

        worker = JavaDownloadWorker(major, self)
        self._workers[major] = worker

        def on_progress(m, percent):
            if m == major:
                row["progress"].setValue(int(percent))
                row["status"].setText(f"скачивание… {int(percent)}%")

        def on_done(m, path):
            row["progress"].setValue(100)
            row["progress"].hide()
            row["status"].setText("установлена")
            row["button"].setText("Переустановить")
            row["button"].setEnabled(True)
            worker.deleteLater()
            self._workers.pop(major, None)
            self.refresh()

        def on_failed(m, error):
            row["progress"].hide()
            row["status"].setText(f"ошибка: {error}")
            row["button"].setText("Скачать")
            row["button"].setEnabled(True)
            worker.deleteLater()
            self._workers.pop(major, None)

        worker.progress.connect(on_progress)
        worker.done.connect(on_done)
        worker.failed.connect(on_failed)
        worker.start()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
        try:
            from ui.animations import fade_in

            fade_in(self, duration=200)
        except Exception:
            pass
