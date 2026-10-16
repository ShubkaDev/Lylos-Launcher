"""Встроенные скины по умолчанию: Steve (classic) и Alex (slim).

Если у аккаунта нет скина, лаунчер назначает случайный встроенный скин
(Steve или Alex), чтобы персонаж всегда выглядел «как в Minecraft» —
и в лаунчере, и в игре (через CustomSkinLoader).

Скины генерируются программно в виде PNG 64x64 (без внешних файлов),
поэтому работают офлайн и не требуют скачивания.
"""

from __future__ import annotations

import random
import struct
import zlib
from typing import Any

# --- палитра ---------------------------------------------------------------
SKIN_TONE = (198, 139, 92)        # классический тон кожи Steve
SKIN_TONE_ALEX = (222, 173, 128)  # чуть светлее у Alex
HAIR = (58, 42, 30)               # тёмно-коричневые волосы Steve
HAIR_ALEX = (160, 82, 45)         # рыжеватые волосы Alex
SHIRT_STEVE = (0, 168, 168)       # бирюзовая рубашка Steve
SHIRT_ALEX = (0, 168, 84)         # зелёная рубашка Alex
PANTS = (59, 68, 170)             # синие штаны
SHOES = (74, 74, 74)              # серые ботинки
EYE_WHITE = (255, 255, 255)
EYE_PUPIL = (63, 118, 228)
MOUTH = (120, 70, 40)
NOSE = (170, 110, 70)
TRANSPARENT = (0, 0, 0, 0)


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    chunk = tag + data
    return (
        struct.pack(">I", len(data))
        + chunk
        + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)
    )


class _SkinBuilder:
    """Простой построитель PNG-скина 64x64 (RGBA)."""

    def __init__(self) -> None:
        self.pixels: list[list[tuple[int, int, int, int]]] = [
            [TRANSPARENT for _ in range(64)] for _ in range(64)
        ]

    def fill(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int, int]) -> None:
        for yy in range(y, y + h):
            row = self.pixels[yy]
            for xx in range(x, x + w):
                row[xx] = color

    def png(self) -> bytes:
        raw = bytearray()
        for row in self.pixels:
            raw.append(0)  # filter: None
            for color in row:
                if len(color) == 3:
                    r, g, b = color
                    a = 255
                else:
                    r, g, b, a = color
                raw += bytes((r, g, b, a))
        ihdr = struct.pack(">IIBBBBB", 64, 64, 8, 6, 0, 0, 0)
        return (
            b"\x89PNG\r\n\x1a\n"
            + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", zlib.compress(bytes(raw)))
            + _png_chunk(b"IEND", b"")
        )


def _draw_head(b: _SkinBuilder, skin: tuple, hair: tuple) -> None:
    """Голова: верх, бока, зад и лицо с глазами/носом/ртом."""
    # верх головы
    b.fill(32, 0, 8, 8, hair)
    # правая сторона
    b.fill(0, 0, 8, 2, hair)
    b.fill(0, 2, 8, 6, skin)
    # левая сторона
    b.fill(16, 0, 8, 2, hair)
    b.fill(16, 2, 8, 6, skin)
    # зад
    b.fill(24, 0, 8, 2, hair)
    b.fill(24, 2, 8, 6, skin)
    # лицо
    b.fill(8, 0, 8, 2, hair)      # чёлка
    b.fill(8, 2, 1, 6, hair)      # левый край волос
    b.fill(15, 2, 1, 6, hair)     # правый край волос
    b.fill(9, 2, 6, 6, skin)      # лицо
    # глаза
    b.fill(10, 4, 2, 2, EYE_WHITE)
    b.fill(12, 4, 2, 2, EYE_WHITE)
    b.fill(10, 4, 1, 2, EYE_PUPIL)
    b.fill(13, 4, 1, 2, EYE_PUPIL)
    # нос
    b.fill(11, 5, 2, 1, NOSE)
    # рот
    b.fill(10, 6, 4, 1, MOUTH)


def _draw_body(b: _SkinBuilder, shirt: tuple) -> None:
    b.fill(20, 8, 8, 8, shirt)   # перед
    b.fill(16, 8, 4, 8, shirt)   # правая сторона
    b.fill(28, 8, 4, 8, shirt)   # левая сторона
    b.fill(32, 8, 8, 8, shirt)   # зад


def _draw_arms(b: _SkinBuilder, skin: tuple, shirt: tuple) -> None:
    # перед левой/правой руки
    for x in (36, 44):
        b.fill(x, 16, 4, 8, shirt)
        b.fill(x, 24, 4, 8, skin)
    # боковые части рук
    for x in (32, 40):
        b.fill(x, 16, 4, 8, shirt)
        b.fill(x, 24, 4, 8, skin)


def _draw_legs(b: _SkinBuilder) -> None:
    # перед левой/правой ноги
    for x in (0, 4):
        b.fill(x, 16, 4, 12, PANTS)
        b.fill(x, 28, 4, 4, SHOES)
    # боковые части ног
    for x in (8, 12):
        b.fill(x, 16, 4, 12, PANTS)
        b.fill(x, 28, 4, 4, SHOES)


def _build_steve() -> _SkinBuilder:
    b = _SkinBuilder()
    _draw_head(b, SKIN_TONE, HAIR)
    _draw_body(b, SHIRT_STEVE)
    _draw_arms(b, SKIN_TONE, SHIRT_STEVE)
    _draw_legs(b)
    return b


def _build_alex() -> _SkinBuilder:
    b = _SkinBuilder()
    _draw_head(b, SKIN_TONE_ALEX, HAIR_ALEX)
    _draw_body(b, SHIRT_ALEX)
    _draw_arms(b, SKIN_TONE_ALEX, SHIRT_ALEX)
    _draw_legs(b)
    return b


def _find_asset_skin(name: str) -> Path | None:
    """Найти PNG скина в assets/skins/{stiv|aleks}.

    Пользователь может положить свои PNG-скины в папки
    ``assets/skins/stiv`` (Steve) и ``assets/skins/aleks`` (Alex) —
    лаунчер возьмёт первый PNG из нужной папки. Если файлов нет,
    используется программная генерация (см. ``builtin_skin_png``).
    """
    try:
        from pathlib import Path

        root = Path(__file__).resolve().parents[1] / "assets" / "skins"
        folder = "stiv" if str(name).lower() == "steve" else "aleks"
        folder_path = root / folder
        if not folder_path.is_dir():
            return None
        for path in sorted(folder_path.glob("*.png")):
            if path.is_file():
                return path
    except Exception:
        return None
    return None


def builtin_skin_png(name: str) -> bytes:
    """PNG-байты встроенного скина: 'steve' или 'alex'.

    Сначала ищется PNG в assets/skins/{stiv|aleks}; если файл найден —
    используются его байты, иначе скин генерируется программно.
    """
    asset = _find_asset_skin(name)
    if asset is not None:
        try:
            return asset.read_bytes()
        except Exception:
            pass
    if str(name).lower() == "alex":
        return _build_alex().png()
    return _build_steve().png()


def ensure_default_skin(account: dict[str, Any] | None) -> dict[str, Any] | None:
    """Если у аккаунта нет скина — назначить случайный Steve/Alex.

    Возвращает обновлённый аккаунт (или None, если скин уже был / ошибка).
    Скин не назначается повторно, если пользователь сам убрал его
    (флаг ``skin_cleared`` в аккаунте).
    """
    if not account or not account.get("id"):
        return None
    if account.get("skin_cleared"):
        return None

    from core.skin_manager import SkinManager

    skins = SkinManager()
    try:
        if skins.get_account_skin(account):
            return None
    except Exception:
        return None

    choice = random.choice(("steve", "alex"))
    try:
        skin = skins.get_or_create_builtin_skin(choice)
        return skins.set_account_skin(
            account["id"],
            skin["id"],
            "classic" if choice == "steve" else "slim",
        )
    except Exception:
        return None