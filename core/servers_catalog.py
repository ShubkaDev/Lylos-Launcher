"""Каталог Minecraft-серверов для страницы «Сервера».

Источники:
1. Удалённый «servers.json» с сайта лаунчера (если доступен) — позволяет
   обновлять список без пересборки.
2. Встроенный assets/servers.json — всегда доступен даже без интернета.

Живые статусы (онлайн, игроки, версия) подтягиваются с mcsrvstat.us.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from core.app_info import WEBSITE_RELEASE_JSON_URL
from core.constants import USER_AGENT

MCSRVSTAT_URL = "https://api.mcsrvstat.us/3/{}"


def _resource_path() -> Path:
    """Путь к ресурсам: в PyInstaller — из _MEIPASS, иначе из проекта."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[1]


def _bundled_path() -> Path:
    return _resource_path() / "assets" / "servers.json"


def _remote_servers_url() -> str:
    """URL удалённого списка серверов (по умолчанию рядом с release.json)."""
    configured = os.environ.get("SM_WEBSITE_SERVERS_URL", "").strip()
    if configured:
        return configured
    base = (WEBSITE_RELEASE_JSON_URL or "").strip()
    for suffix in ("release.json",):
        if base.endswith(suffix):
            return base[: -len(suffix)] + "servers.json"
    return base


def _load_entries_from_text(text: str) -> list[dict]:
    data = json.loads(text or "[]")
    if isinstance(data, dict):
        data = data.get("servers") or data.get("data") or []
    entries = []
    for raw in data or []:
        if not isinstance(raw, dict):
            continue
        host = str(raw.get("host") or raw.get("address") or "").strip()
        if not host:
            continue
        try:
            port = int(raw.get("port") or 25565)
        except (TypeError, ValueError):
            port = 25565
        entries.append(
            {
                "name": str(raw.get("name") or host).strip() or host,
                "host": host,
                "port": port,
                "region": str(raw.get("region") or "🌍 Мир").strip(),
                "description": str(raw.get("description") or "").strip(),
            }
        )
    return entries


def _load_bundled() -> list[dict]:
    path = _bundled_path()
    if not path.exists():
        return []
    try:
        return _load_entries_from_text(path.read_text(encoding="utf-8"))
    except Exception:
        traceback.print_exc()
        return []


def _load_remote(timeout: float = 6.0) -> list[dict] | None:
    url = _remote_servers_url()
    if not url or not url.startswith("http"):
        return None
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
        )
        response.raise_for_status()
        entries = _load_entries_from_text(response.text)
        return entries or None
    except Exception:
        return None


def _check_status(server: dict, timeout: float = 7.0) -> dict:
    """Проверяет статус сервера через mcsrvstat.us."""
    host = str(server.get("host") or "").strip()
    server["online"] = False
    server["players"] = 0
    server["max_players"] = 0
    server["version"] = ""
    server["source"] = "mcsrvstat"

    if not host:
        return server

    port = int(server.get("port") or 25565)
    address = f"{host}:{port}" if port != 25565 else host
    server["address"] = address
    server["link"] = f"https://namemc.com/server/{host}"

    try:
        response = requests.get(
            MCSRVSTAT_URL.format(address),
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json() or {}
        server["online"] = bool(data.get("online"))
        players = data.get("players") or {}
        server["players"] = int(players.get("online") or 0)
        server["max_players"] = int(players.get("max") or 0)
        version = data.get("version") or ""
        if isinstance(version, dict):
            version = version.get("name") or ""
        if version:
            server["version"] = str(version)
    except Exception:
        server["online"] = False
    return server


def _enrich_with_status(servers: list[dict], timeout: float = 7.0) -> list[dict]:
    """Параллельно проверяет статусы всех серверов списка."""
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(_check_status, dict(s), timeout) for s in servers]
        results = []
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception:
                results.append({"online": False})
    return results


def fetch_top_servers(limit: int = 100, timeout: float = 20.0) -> list[dict]:
    """Возвращает список серверов с живыми статусами.

    Запись: {name, host, port, address, players, max_players, version,
    online, region, description, source, link}.
    """
    entries = _load_remote(timeout=min(timeout, 6.0)) or _load_bundled()
    if not entries:
        return []

    try:
        limit = max(int(limit), 1)
    except (TypeError, ValueError):
        limit = 100
    entries = entries[:limit]

    status_timeout = min(max(timeout - 6.0, 4.0), 8.0)
    enriched = _enrich_with_status(entries, timeout=status_timeout)
    enriched.sort(key=lambda s: s.get("players", 0), reverse=True)
    return enriched