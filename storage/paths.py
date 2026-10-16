from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "Lylos Launcher"
LEGACY_APP_DIR_NAME = "SMLauncher"


def _project_root() -> Path:
    # storage/paths.py -> project root
    return Path(__file__).resolve().parents[1]


def _appdata_root() -> Path:
    appdata = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    current_root = appdata / APP_DIR_NAME
    legacy_root = appdata / LEGACY_APP_DIR_NAME
    legacy_data = legacy_root / "data"
    current_data = current_root / "data"

    if legacy_data.is_dir() and not current_data.exists():
        try:
            current_root.mkdir(parents=True, exist_ok=True)
            legacy_data.rename(current_data)
        except OSError:
            return legacy_root

    return current_root


def get_base_dir() -> Path:
    """
    Единая корневая папка данных лаунчера.

    В режиме разработки данные лежат рядом с проектом, независимо от того,
    из какой папки был запущен python. В собранном .exe данные лежат в AppData,
    чтобы лаунчер мог работать из Program Files/Downloads без прав администратора.
    """
    if getattr(sys, "frozen", False):
        return _appdata_root()
    return _project_root()


BASE_DIR = get_base_dir()
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
INSTANCES_DIR = DATA_DIR / "instances"
INSTANCES_FILE = INSTANCES_DIR / "instances.json"
STORAGE_DIR = DATA_DIR / "storage"
MODS_DIR = DATA_DIR / "mods"
SKINS_DIR = DATA_DIR / "skins"


def ensure_project_dirs():
    for directory in [DATA_DIR, LOGS_DIR, INSTANCES_DIR, STORAGE_DIR, MODS_DIR, SKINS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
