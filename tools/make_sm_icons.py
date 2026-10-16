"""Generate the SMLauncher brand icon set (PNG + ICO + website assets).

Run:  .venv\\Scripts\\python.exe tools\\make_sm_icons.py
"""
import os
import struct
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QImage, QLinearGradient,
                           QPainter, QPainterPath, QPen, QRadialGradient)
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]

VIOLET = "#8B5CF6"
VIOLET_DEEP = "#7C3AED"
CYAN = "#06B6D4"
WHITE = "#FFFFFF"


def render_tile(size: int) -> QImage:
    """Rounded-square tile with violet->cyan gradient and bold 'LL'."""
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    margin = max(2.0, size * 0.04)
    r = size * 0.19
    rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
    grad.setColorAt(0.0, QColor(VIOLET))
    grad.setColorAt(0.55, QColor(VIOLET_DEEP))
    grad.setColorAt(1.0, QColor(CYAN))
    path = QPainterPath()
    path.addRoundedRect(rect, r, r)
    p.fillPath(path, QBrush(grad))
    pen = QPen(QColor(255, 255, 255, 95))
    pen.setWidthF(max(1.2, size * 0.005))
    p.setPen(pen)
    p.drawPath(path)
    font = QFont("Segoe UI")
    font.setWeight(QFont.Weight.Black)
    font.setPixelSize(int(size * 0.40))
    p.setFont(font)
    p.setPen(QColor(WHITE))
    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "LL")
    p.end()
    return img


def render_cover() -> QImage:
    """1200x630 social cover: dark bg, glow, tile + wordmark."""
    w, h = 1200, 630
    img = QImage(w, h, QImage.Format_ARGB32)
    img.fill(QColor("#0B0E1A"))
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    g1 = QLinearGradient(0, 0, w, h)
    g1.setColorAt(0.0, QColor("#0B0E1A"))
    g1.setColorAt(0.55, QColor("#161032"))
    g1.setColorAt(1.0, QColor("#082030"))
    p.fillRect(0, 0, w, h, QBrush(g1))
    # glows
    glow1 = QRadialGradient(w * 0.22, h * 0.35, w * 0.5)
    glow1.setColorAt(0.0, QColor(139, 92, 246, 130))
    glow1.setColorAt(1.0, QColor(139, 92, 246, 0))
    p.fillRect(0, 0, w, h, QBrush(glow1))
    glow2 = QRadialGradient(w * 0.78, h * 0.55, w * 0.45)
    glow2.setColorAt(0.0, QColor(6, 182, 212, 110))
    glow2.setColorAt(1.0, QColor(6, 182, 212, 0))
    p.fillRect(0, 0, w, h, QBrush(glow2))
    # tile
    tile_size = 250
    tile = render_tile(tile_size)
    p.drawImage(90, h // 2 - tile_size // 2, tile)
    # wordmark
    font = QFont("Segoe UI")
    font.setWeight(QFont.Weight.Black)
    font.setPixelSize(84)
    p.setFont(font)
    p.setPen(QColor("#F4F6FF"))
    p.drawText(QRectF(400, h // 2 - 118, 720, 110), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Lylos Launcher")
    sub = QFont("Segoe UI")
    sub.setWeight(QFont.Weight.DemiBold)
    sub.setPixelSize(30)
    p.setFont(sub)
    p.setPen(QColor("#94A3B8"))
    p.drawText(QRectF(402, h // 2 + 8, 720, 60), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
               "Minecraft лаунчер для Windows · сборки · моды · шейдеры")
    p.end()
    return img


def make_ico(images):
    """Build a Windows .ico container from a list of (size, png_bytes)."""
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries = b""
    payload = b""
    for size, png in images:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset)
        offset += len(png)
        payload += png
    return header + entries + payload


def png_bytes(img: QImage) -> bytes:
    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    if not img.save(buf, "PNG"):
        raise RuntimeError("Failed to encode PNG")
    buf.close()
    return bytes(ba)


def main():
    app = QApplication([])  # offscreen platform

    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "icons").mkdir(exist_ok=True)
    (ROOT / "website" / "assets").mkdir(exist_ok=True)

    # Big PNGs
    (ROOT / "assets" / "LL.png").write_bytes(png_bytes(render_tile(1024)))
    (ROOT / "assets" / "icons" / "LL.png").write_bytes(png_bytes(render_tile(512)))
    (ROOT / "website" / "assets" / "logo.png").write_bytes(png_bytes(render_tile(512)))
    (ROOT / "website" / "assets" / "favicon.png").write_bytes(png_bytes(render_tile(128)))
    (ROOT / "website" / "assets" / "og-cover.png").write_bytes(png_bytes(render_cover()))
    print("PNG assets written")

    # Multi-size ICO
    sizes = (16, 24, 32, 48, 64, 128, 256)
    ico = make_ico([(s, png_bytes(render_tile(s))) for s in sizes])
    (ROOT / "assets" / "LL.ico").write_bytes(ico)
    print("assets/LL.ico written (%d bytes)" % len(ico))


if __name__ == "__main__":
    main()