"""Импорт миров и модов из ZIP/JAR-архивов в сборку.

Логика:
  - «Добавить мир»: пользователь выбирает ZIP. Лаунчер распаковывает архив
    (и вложенные архивы рекурсивно), находит папки миров (содержат level.dat)
    и копирует их в ``saves/`` сборки. Все вложенные ZIP, которые лаунчер
    распаковал, удаляются; исходный архив пользователя остаётся на месте.
  - «Добавить мод»: пользователь выбирает ZIP или JAR. Из ZIP рекурсивно
    извлекаются JAR-файлы и копируются в ``mods/`` сборки. Вложенные ZIP
    удаляются, исходный файл пользователя не трогается.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Расширения, которые умеет распаковывать zipfile (ZIP-совместимые).
ZIP_SUFFIXES = {".zip", ".jar"}


def _is_zip(path: Path) -> bool:
    try:
        return path.suffix.lower() in ZIP_SUFFIXES and zipfile.is_zipfile(path)
    except Exception:
        return False


def _safe_extract(zf: zipfile.ZipFile, member, target_dir: Path) -> None:
    """Извлечь member с защитой от path traversal."""
    member_path = Path(member.filename)
    if member_path.is_absolute() or ".." in member_path.parts:
        raise RuntimeError(f"Обнаружен небезопасный путь в архиве: {member.filename}")
    zf.extract(member, target_dir)


def _extract_nested(root: Path, extracted_zips: list[Path]) -> list[Path]:
    """Рекурсивно распаковать все ZIP-архивы внутри ``root``.

    Возвращает список распакованных (вложенных) архивов — их потом удаляют.
    """
    found: list[Path] = []
    changed = True
    while changed:
        changed = False
        for archive in sorted(root.rglob("*")):
            if not archive.is_file() or not _is_zip(archive):
                continue
            if archive in extracted_zips:
                continue
            try:
                with zipfile.ZipFile(archive, "r") as zf:
                    for member in zf.infolist():
                        _safe_extract(zf, member, archive.parent)
            except Exception as error:
                logger.warning("Не удалось распаковать вложенный архив %s: %s", archive, error)
                continue
            extracted_zips.append(archive)
            found.append(archive)
            changed = True
    return found


def _find_world_folders(root: Path) -> list[Path]:
    """Папки миров Minecraft: содержат level.dat."""
    worlds: list[Path] = []
    for level_dat in root.rglob("level.dat"):
        folder = level_dat.parent
        if folder not in worlds:
            worlds.append(folder)
    return worlds


def _unique_target(directory: Path, name: str) -> Path:
    """Имя файла/папки без перезаписи существующего."""
    target = directory / name
    stem = Path(name).stem
    suffix = Path(name).suffix
    counter = 2
    while target.exists():
        target = directory / f"{stem} ({counter}){suffix}"
        counter += 1
    return target


def import_worlds(instance: dict, archive_path: str | Path) -> dict:
    """Распаковать архив и скопировать миры в ``saves/`` сборки.

    Возвращает {"worlds": [...], "deleted_zips": [...]}.
    """
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise RuntimeError("Файл не найден.")
    if not _is_zip(archive_path):
        raise RuntimeError("Выбери ZIP-архив с мирами.")

    minecraft_dir = Path(
        instance.get("minecraft_dir") or Path(instance.get("path", "")) / ".minecraft"
    )
    saves_dir = minecraft_dir / "saves"
    saves_dir.mkdir(parents=True, exist_ok=True)

    temp_dir = Path(tempfile.mkdtemp(prefix="sm_worlds_"))
    extracted_zips: list[Path] = []
    try:
        # Распаковка исходного архива.
        with zipfile.ZipFile(archive_path, "r") as zf:
            for member in zf.infolist():
                _safe_extract(zf, member, temp_dir)

        # Рекурсивно распаковываем вложенные архивы.
        nested = _extract_nested(temp_dir, extracted_zips)

        worlds = _find_world_folders(temp_dir)
        if not worlds:
            raise RuntimeError("В архиве не найдены папки миров (нет level.dat).")

        imported = []
        for world in worlds:
            target = _unique_target(saves_dir, world.name)
            shutil.copytree(world, target)
            imported.append(target.name)

        # Удаляем вложенные архивы, которые распаковали (исходный не трогаем).
        for zip_path in nested:
            try:
                zip_path.unlink(missing_ok=True)
            except Exception:
                pass

        return {"worlds": imported, "deleted_zips": [p.name for p in nested]}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def import_mods(instance: dict, file_path: str | Path) -> dict:
    """Скопировать JAR-моды в ``mods/`` сборки.

    Если выбран ZIP — рекурсивно распаковывается до JAR-файлов.
    Если выбран JAR — просто копируется.

    Возвращает {"mods": [...], "deleted_zips": [...]}.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise RuntimeError("Файл не найден.")

    minecraft_dir = Path(
        instance.get("minecraft_dir") or Path(instance.get("path", "")) / ".minecraft"
    )
    mods_dir = minecraft_dir / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)

    # Прямой JAR — просто копируем.
    if file_path.suffix.lower() == ".jar":
        target = _unique_target(mods_dir, file_path.name)
        shutil.copy2(file_path, target)
        return {"mods": [target.name], "deleted_zips": []}

    if not _is_zip(file_path):
        raise RuntimeError("Выбери JAR-файл мода или ZIP-архив с модами.")

    temp_dir = Path(tempfile.mkdtemp(prefix="sm_mods_"))
    extracted_zips: list[Path] = []
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            for member in zf.infolist():
                _safe_extract(zf, member, temp_dir)

        nested = _extract_nested(temp_dir, extracted_zips)

        jars = [p for p in temp_dir.rglob("*.jar") if p.is_file()]
        if not jars:
            raise RuntimeError("В архиве не найдены JAR-файлы модов.")

        imported = []
        for jar in jars:
            target = _unique_target(mods_dir, jar.name)
            shutil.copy2(jar, target)
            imported.append(target.name)

        for zip_path in nested:
            try:
                zip_path.unlink(missing_ok=True)
            except Exception:
                pass

        return {"mods": imported, "deleted_zips": [p.name for p in nested]}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)