"""Automatic managed Java runtime installation for SMLauncher.

Downloads a Temurin JRE for Windows x64 from the Adoptium API into
``%LOCALAPPDATA%\\SM\\java\\{major}\\runtime``. ``core.java_manager`` already
scans that folder (``*/bin/java.exe``), so after installation the launcher
finds the required Java automatically on the next launch attempt.
"""
from __future__ import annotations

import logging
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

ADOPTIUM_BINARY_API = (
    "https://api.adoptium.net/v3/binary/latest/{major}/ga/windows/x64/jre/hotspot/normal/eclipse"
)
USER_AGENT = "LylosLauncher/1.0"
TIMEOUT = 60


def managed_java_dir(major: int) -> Path:
    base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    return base / "SM" / "java" / str(major)


def find_managed_java(major: int) -> Path | None:
    """Return path to bin/java.exe for a managed runtime, if installed."""
    java_exe = managed_java_dir(major) / "bin" / "java.exe"
    if java_exe.is_file():
        return java_exe

    root = managed_java_dir(major)
    if root.is_dir():
        candidates = sorted(root.glob("*/bin/java.exe"))
        if candidates:
            return candidates[0]
    return None


def _open(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(request, timeout=TIMEOUT)


def download_managed_java(major: int, progress_callback=None) -> Path:
    """Download and extract Temurin JRE {major}; return path to bin/java.exe.

    If a managed runtime for this major already exists it is returned without
    any network activity.
    """
    progress_callback = progress_callback or (lambda downloaded, total: None)

    existing = find_managed_java(major)
    if existing:
        return existing

    target_dir = managed_java_dir(major)
    target_dir.mkdir(parents=True, exist_ok=True)

    zip_path = target_dir / f"temurin-{major}.zip"
    tmp_zip = zip_path.with_suffix(".zip.tmp")
    extract_dir = target_dir / "extract"
    runtime_dir = target_dir / "runtime"

    try:
        # ---- download ----
        with _open(ADOPTIUM_BINARY_API.format(major=major)) as response:
            total = int(response.headers.get("content-length") or 0)
            downloaded = 0
            with open(tmp_zip, "wb") as output:
                while True:
                    chunk = response.read(1024 * 256)
                    if not chunk:
                        break
                    output.write(chunk)
                    downloaded += len(chunk)
                    progress_callback(downloaded, total)

        if tmp_zip.stat().st_size <= 0:
            raise RuntimeError("Скачанный архив Java пуст.")
        tmp_zip.replace(zip_path)

        # ---- extract ----
        if extract_dir.exists():
            shutil.rmtree(extract_dir, ignore_errors=True)
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(extract_dir)

        subdirs = [path for path in extract_dir.iterdir() if path.is_dir()]
        if not subdirs:
            raise RuntimeError("Архив Java не содержит папки с рантаймом.")

        if runtime_dir.exists():
            shutil.rmtree(runtime_dir, ignore_errors=True)
        shutil.move(str(subdirs[0]), str(runtime_dir))

        java_exe = runtime_dir / "bin" / "java.exe"
        if not java_exe.is_file():
            raise RuntimeError(f"В архиве нет bin/java.exe: {java_exe}")

        logger.info("Managed Java %s installed at %s", major, java_exe)
        return java_exe

    except Exception:
        logger.exception("Failed to install managed Java %s", major)
        raise
    finally:
        for leftover in (tmp_zip, zip_path):
            try:
                leftover.unlink(missing_ok=True)
            except Exception:
                pass
        shutil.rmtree(extract_dir, ignore_errors=True)


def ensure_managed_java(major: int, progress_callback=None) -> Path | None:
    """Return a usable managed java.exe for ``major`` or None on failure."""
    try:
        return download_managed_java(major, progress_callback=progress_callback)
    except Exception as error:
        logger.error("ensure_managed_java(%s) failed: %s", major, error)
        return None