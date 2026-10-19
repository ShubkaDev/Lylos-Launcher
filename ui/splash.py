"""Lylos Launcher splash screen: Minecraft panorama, animated loading, update check.

The splash picks a random panorama from ``assets/panorama`` on every launch,
shows the launcher name with a violet->cyan gradient, an animated progress bar
and a status line („Проверка обновления...“ / „Загрузка...“).
"""
from __future__ import annotations

import logging
import random
import sys
from pathlib import Path

from PySide6.QtCore import QRectF, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QWidget

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PANORAMA_DIR = PROJECT_ROOT / "assets" / "panorama"

SPLASH_W = 960
SPLASH_H = 540

VIOLET = "#8B5CF6"
VIOLET_DEEP = "#7C3AED"
CYAN = "#22D3EE"


def _pick_panorama() -> Path | None:
    """Return a random panorama image path (or None if the folder is empty)."""
    try:
        images = [
            path
            for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp")
            for path in PANORAMA_DIR.glob(pattern)
            if path.is_file()
        ]
        if not images:
            return None
        return random.choice(sorted(images, key=lambda p: p.name.lower()))
    except Exception:
        return None


class SplashScreen(QWidget):
    """Frameless, rounded splash window with a random Minecraft panorama."""

    def __init__(self):
        super().__init__()
        self.setObjectName("SplashScreen")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(SPLASH_W, SPLASH_H)

        self._panorama = QPixmap()
        panorama_path = _pick_panorama()
        if panorama_path:
            loaded = QPixmap(str(panorama_path))
            if not loaded.isNull():
                self._panorama = loaded
        self._pan_offset = 0.0
        self._status_text = "Проверка обновления..."
        self._version_text = ""
        self._progress = 0.0
        self._glow_x = 0.0
        self._loading_timer = QTimer(self)
        self._loading_timer.setInterval(16)
        self._loading_timer.timeout.connect(self._tick)
        self._pan_timer = QTimer(self)
        self._pan_timer.setInterval(33)
        self._pan_timer.timeout.connect(self._pan_tick)
        self._pan_timer.start()

        try:
            from core.app_info import APP_FULL_NAME
            self._version_text = APP_FULL_NAME
        except Exception:
            self._version_text = "Lylos Launcher"

        self._on_loading_done = None
        self._center_on_screen()

    # ------------------------------------------------------------------ API
    def set_status(self, text: str):
        self._status_text = text
        self.update()

    def set_progress(self, fraction: float):
        """0..1 progress (used while downloading an update)."""
        self._progress = max(0.0, min(1.0, fraction))
        self.update()

    def play_loading(self, duration_ms: int, on_done=None):
        """Animate the progress bar 0->100% over ``duration_ms``."""
        self._on_loading_done = on_done
        self._progress = 0.0
        self._loading_step = 100.0 / max(duration_ms / 16.0, 1.0)
        self._loading_timer.start()

    # ------------------------------------------------------------- internal
    def _center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        self.move(geo.center().x() - self.width() // 2, geo.center().y() - self.height() // 2)

    def _tick(self):
        self._progress += self._loading_step
        if self._progress >= 100.0:
            self._progress = 100.0
            self._loading_timer.stop()
            callback = self._on_loading_done
            self._on_loading_done = None
            if callback:
                callback()
        self.update()

    def _pan_tick(self):
        if self._panorama.isNull():
            return
        self._pan_offset = (self._pan_offset + 0.4) % 10000.0
        self.update()

    # ------------------------------------------------------------- painting
    def _draw_panorama(self, painter: QPainter):
        rect = self.rect()
        if self._panorama.isNull():
            # Fallback: violet/cyan space gradient
            gradient = QLinearGradient(0, 0, rect.width(), rect.height())
            gradient.setColorAt(0.0, QColor("#0B0E1A"))
            gradient.setColorAt(0.5, QColor("#1E1445"))
            gradient.setColorAt(1.0, QColor("#083044"))
            painter.fillRect(rect, gradient)
            return

        img: QImage = self._panorama.toImage()
        scale = max(rect.height() / max(img.height(), 1), rect.width() / max(img.width(), 1))
        draw_w = img.width() * scale
        draw_h = img.height() * scale

        max_offset = max(draw_w - rect.width(), 0.0)
        if max_offset > 0:
            cycle = max_offset * 2.0
            x = (self._pan_offset % cycle)
            if x > max_offset:
                x = cycle - x
            x = -x
        else:
            x = 0.0

        y = (rect.height() - draw_h) / 2.0
        painter.drawImage(QRectF(x, y, draw_w, draw_h), img)

        # Readability overlay
        overlay = QLinearGradient(0, 0, 0, rect.height())
        overlay.setColorAt(0.0, QColor(5, 8, 18, 90))
        overlay.setColorAt(0.45, QColor(5, 8, 18, 40))
        overlay.setColorAt(1.0, QColor(5, 8, 18, 200))
        painter.fillRect(rect, overlay)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 28, 28)
        painter.setClipPath(path)

        self._draw_panorama(painter)

        w = self.width()

        # --- Brand mark ---
        mark_size = 64
        mark_rect = QRectF(w / 2 - mark_size / 2, 92, mark_size, mark_size)
        grad = QLinearGradient(mark_rect.topLeft(), mark_rect.bottomRight())
        grad.setColorAt(0.0, QColor(VIOLET))
        grad.setColorAt(0.55, QColor(VIOLET_DEEP))
        grad.setColorAt(1.0, QColor(CYAN))
        painter.setBrush(grad)
        painter.setPen(QPen(QColor(255, 255, 255, 90), 1.5))
        painter.drawRoundedRect(mark_rect, 18, 18)
        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.Black)
        font.setPixelSize(26)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(mark_rect, Qt.AlignmentFlag.AlignCenter, "LL")

        # --- Title ---
        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.Black)
        font.setPixelSize(52)
        painter.setFont(font)
        title_rect = QRectF(0, 168, w, 66)
        title_grad = QLinearGradient(0, 0, w, 0)
        title_grad.setColorAt(0.0, QColor("#F4F6FF"))
        title_grad.setColorAt(0.5, QColor("#D8C9FF"))
        title_grad.setColorAt(1.0, QColor("#7DE9F8"))
        painter.setPen(QPen(title_grad, 1))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, "Lylos Launcher")

        # --- Subtitle ---
        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.DemiBold)
        font.setPixelSize(15)
        painter.setFont(font)
        painter.setPen(QColor("#C7D2FE"))
        painter.drawText(
            QRectF(0, 234, w, 30),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            "Minecraft лаунчер для Windows",
        )

        # --- Progress bar ---
        bar_w = 420
        bar_h = 8
        bar_x = w / 2 - bar_w / 2
        bar_y = 396
        bar_rect = QRectF(bar_x, bar_y, bar_w, bar_h)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 36))
        painter.drawRoundedRect(bar_rect, bar_h / 2, bar_h / 2)

        if self._progress > 0:
            fill_w = max(bar_h, bar_w * self._progress / 100.0)
            fill_rect = QRectF(bar_x, bar_y, fill_w, bar_h)
            fill_grad = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            fill_grad.setColorAt(0.0, QColor(VIOLET))
            fill_grad.setColorAt(1.0, QColor(CYAN))
            painter.setBrush(fill_grad)
            painter.drawRoundedRect(fill_rect, bar_h / 2, bar_h / 2)

            # shimmering highlight
            glow = QLinearGradient(bar_x + fill_w - 60, 0, bar_x + fill_w + 20, 0)
            glow.setColorAt(0.0, QColor(255, 255, 255, 0))
            glow.setColorAt(0.5, QColor(255, 255, 255, 130))
            glow.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setBrush(glow)
            painter.drawRoundedRect(
                QRectF(max(bar_x, bar_x + fill_w - 60), bar_y, min(80.0, bar_w - fill_w + 60), bar_h),
                bar_h / 2, bar_h / 2,
            )
        elif not self._loading_timer.isActive():
            # idle shimmer while waiting for network
            from time import monotonic
            phase = (monotonic() * 2.0) % 1.0
            segment_w = 120.0
            seg_x = bar_x + phase * (bar_w - segment_w)
            shimmer = QLinearGradient(seg_x, 0, seg_x + segment_w, 0)
            shimmer.setColorAt(0.0, QColor(255, 255, 255, 0))
            shimmer.setColorAt(0.5, QColor(255, 255, 255, 70))
            shimmer.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setBrush(shimmer)
            painter.drawRoundedRect(QRectF(seg_x, bar_y, segment_w, bar_h), bar_h / 2, bar_h / 2)

        # --- Status text ---
        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.Bold)
        font.setPixelSize(14)
        painter.setFont(font)
        painter.setPen(QColor("#E2E8F0"))
        painter.drawText(
            QRectF(0, 416, w, 30),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            self._status_text,
        )

        # --- Version ---
        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.DemiBold)
        font.setPixelSize(12)
        painter.setFont(font)
        painter.setPen(QColor(148, 163, 184, 200))
        painter.drawText(
            QRectF(24, self.height() - 38, w - 48, 24),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self._version_text,
        )

        painter.end()


class UpdateCheckWorker(QThread):
    """Fetch the website release.json and report whether a newer version exists."""

    result_ready = Signal(object)

    def __init__(self, timeout: int = 8, parent=None):
        super().__init__(parent)
        self._timeout = timeout

    def run(self):
        release = None
        try:
            from core.updater import fetch_website_release
            release = fetch_website_release(timeout=self._timeout)
        except Exception:
            logger.debug("Splash update check failed", exc_info=True)
        self.result_ready.emit(release)


class UpdateDownloadWorker(QThread):
    """Download the update asset, reporting progress."""

    progress = Signal(int, int)   # downloaded bytes, total bytes
    done = Signal(str)            # local file path
    failed = Signal(str)

    def __init__(self, asset, parent=None):
        super().__init__(parent)
        self.asset = asset

    def run(self):
        try:
            from core.updater import download_asset
            path = download_asset(self.asset, self._on_progress)
            self.done.emit(str(path))
        except Exception as error:  # noqa: BLE001
            logger.exception("Update download failed")
            self.failed.emit(str(error))

    def _on_progress(self, downloaded: int, total: int, speed: float):
        self.progress.emit(int(downloaded), int(total))


def format_bytes(value: int) -> str:
    size = float(value or 0)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return "—"