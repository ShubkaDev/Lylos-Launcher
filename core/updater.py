from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import quote, urlsplit, urlunsplit

from core.app_info import (
    APP_VERSION,
    GITHUB_LATEST_RELEASE_API,
    GITHUB_LATEST_RELEASE_PAGE,
    GITHUB_OWNER,
    GITHUB_REPO,
    USER_AGENT,
    WEBSITE_RELEASE_JSON_URL,
)
from storage.paths import DATA_DIR


logger = logging.getLogger(__name__)

RETRY_ATTEMPTS = 3
RETRY_DELAY = 1.5
UPDATES_DIR = DATA_DIR / "updates"


@dataclass
class ReleaseAsset:
    name: str
    download_url: str
    size: int | None = None
    content_type: str | None = None


@dataclass
class ReleaseInfo:
    version: str
    tag: str
    name: str
    body: str
    page_url: str
    published_at: str | None
    assets: list[ReleaseAsset]
    preferred_asset: ReleaseAsset | None
    is_newer: bool
    repo: str
    source: str = "github"


def normalize_version(value: str) -> tuple[int, ...]:
    value = (value or "").strip().lower()
    value = value.removeprefix("refs/tags/")
    value = value.removeprefix("v")
    parts = re.findall(r"\d+", value)
    return tuple(int(part) for part in parts) if parts else (0,)


def is_newer_version(remote: str, local: str) -> bool:
    return normalize_version(remote) > normalize_version(local)


def repo_is_configured() -> bool:
    return bool(GITHUB_OWNER and GITHUB_REPO and "YOUR_GITHUB_USERNAME" not in GITHUB_OWNER)


def _encode_url(url: str) -> str:
    """Percent-encode non-ASCII characters in URL path/query.

    urllib/http.client отправляет строку запроса в ASCII и падает с
    ``UnicodeEncodeError`` на кириллице (например, тег релиза «Релизы»).
    """
    parts = urlsplit(str(url or ""))
    path = quote(parts.path, safe="/%:@!$&'()*+,;=-._~")
    query = quote(parts.query, safe="=&%:@!$'()*+,;/?-._~")
    return urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def _request(url: str, timeout: int = 10, accept: str = "application/json"):
    request = urllib.request.Request(
        _encode_url(url),
        headers={
            "Accept": accept,
            "User-Agent": USER_AGENT,
        },
    )
    return urllib.request.urlopen(request, timeout=timeout)


def _request_json(url: str, timeout: int = 10, accept: str = "application/json") -> dict:
    with _request(url, timeout=timeout, accept=accept) as response:
        return json.loads(response.read().decode("utf-8"))


def _request_text(url: str, timeout: int = 10) -> str:
    with _request(url, timeout=timeout, accept="text/plain,*/*") as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_github_latest_release(timeout: int = 10) -> Optional[ReleaseInfo]:
    if not repo_is_configured():
        logger.warning("GitHub repo is not configured: %s/%s", GITHUB_OWNER, GITHUB_REPO)
        return None

    last_error = None

    for attempt in range(RETRY_ATTEMPTS):
        try:
            data = _request_json(
                GITHUB_LATEST_RELEASE_API,
                timeout=timeout,
                accept="application/vnd.github+json",
            )

            tag = data.get("tag_name") or ""
            version = tag.removeprefix("v")
            assets: list[ReleaseAsset] = []

            for asset in data.get("assets") or []:
                url = asset.get("browser_download_url")
                name = asset.get("name")
                if not url or not name:
                    continue

                assets.append(
                    ReleaseAsset(
                        name=str(name),
                        download_url=str(url),
                        size=asset.get("size"),
                        content_type=asset.get("content_type"),
                    )
                )

            preferred_asset = choose_preferred_asset(assets)

            return ReleaseInfo(
                version=version,
                tag=tag or f"v{version}",
                name=data.get("name") or tag or f"Lylos Launcher {version}",
                body=data.get("body") or "",
                page_url=data.get("html_url") or GITHUB_LATEST_RELEASE_PAGE,
                published_at=data.get("published_at"),
                assets=assets,
                preferred_asset=preferred_asset,
                is_newer=is_newer_version(version, APP_VERSION),
                repo=f"{GITHUB_OWNER}/{GITHUB_REPO}",
                source="github",
            )

        except Exception as error:
            last_error = error
            logger.warning("GitHub updater attempt %d/%d failed: %s", attempt + 1, RETRY_ATTEMPTS, error)
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))

    logger.error("All GitHub updater attempts failed: %s", last_error)
    return None


def fetch_website_release(timeout: int = 10) -> Optional[ReleaseInfo]:
    if not WEBSITE_RELEASE_JSON_URL:
        return None

    try:
        data = _request_json(WEBSITE_RELEASE_JSON_URL, timeout=timeout)

        version = str(data.get("version") or "").removeprefix("v")
        if not version:
            return None

        # Ссылка на файл обновления из того же release.json. Поддерживаем и
        # installer .exe, и portable .zip — предпочитаем installer, чтобы
        # можно было обновиться автоматически.
        installer_url = str(
            data.get("installer")
            or data.get("direct_download")
            or data.get("download_url")
            or ""
        ).strip()
        portable_url = str(data.get("portable") or data.get("portable_download") or "").strip()

        if not installer_url.startswith("https://") and not portable_url.startswith("https://"):
            return None

        def _is_valid(url: str) -> bool:
            url = url.lower().split("?", 1)[0]
            return url.startswith("https://") and (url.endswith(".zip") or url.endswith(".exe"))

        assets: list[ReleaseAsset] = []
        if _is_valid(installer_url):
            assets.append(
                ReleaseAsset(
                    name=f"Lylos-Launcher-{version}-win-x64-setup.exe",
                    download_url=installer_url,
                    content_type="application/x-msdownload",
                )
            )
        if _is_valid(portable_url) and portable_url.lower().split("?", 1)[0].endswith(".zip"):
            assets.append(
                ReleaseAsset(
                    name=f"Lylos-Launcher-{version}-win-x64-portable.zip",
                    download_url=portable_url,
                    content_type="application/zip",
                )
            )
        if not assets:
            return None

        preferred_asset = choose_preferred_asset(assets)

        return ReleaseInfo(
            version=version,
            tag=f"v{version}",
            name=str(data.get("name") or f"Lylos Launcher {version}"),
            body=str(data.get("description") or data.get("note") or ""),
            page_url=str(data.get("latest_release_page") or GITHUB_LATEST_RELEASE_PAGE),
            published_at=str(data.get("updated_at") or "") or None,
            assets=assets,
            preferred_asset=preferred_asset,
            is_newer=is_newer_version(version, APP_VERSION),
            repo=str(data.get("repo") or f"{GITHUB_OWNER}/{GITHUB_REPO}"),
            source="website",
        )
    except Exception as error:
        # Website can be unavailable until GitHub Pages finishes deployment.
        # GitHub Releases is the primary update source, so keep this quiet.
        logger.debug("Website release check unavailable: %s", error)
        return None


def fetch_latest_release(timeout: int = 10) -> Optional[ReleaseInfo]:
    """Check update metadata.

    The website ``release.json`` is the source of truth for update checks:
    it is published on GitHub Pages and contains the current version plus
    direct links to the updated files. GitHub Releases API is only a
    fallback when the website is unavailable.
    """

    website_release = fetch_website_release(timeout=timeout)
    if website_release:
        return website_release

    return fetch_github_latest_release(timeout=timeout)


def choose_preferred_asset(assets: list[ReleaseAsset]) -> ReleaseAsset | None:
    if not assets:
        return None

    def score(asset: ReleaseAsset):
        name = asset.name.lower()
        value = 0

        if name.endswith(".sha256"):
            value -= 1000

        if name.endswith(".exe"):
            value += 100

        # Prefer Setup EXE because it can replace the installed app safely.
        if "setup" in name or "installer" in name:
            value += 140

        if "portable" in name and name.endswith(".zip"):
            value += 50

        if "win" in name or "windows" in name:
            value += 25

        if "x64" in name or "amd64" in name:
            value += 15

        return value

    return sorted(assets, key=score, reverse=True)[0]


def is_installer_path(path: str | Path) -> bool:
    name = Path(path).name.lower()
    return name.endswith(".exe") and ("setup" in name or "installer" in name)


def is_archive_path(path: str | Path) -> bool:
    return Path(path).name.lower().endswith(".zip")


def download_asset(asset: ReleaseAsset, progress_callback=None) -> Path:
    progress_callback = progress_callback or (lambda downloaded, total, speed: None)
    UPDATES_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^a-zA-Z0-9_.()\- ]+", "_", asset.name)
    target = UPDATES_DIR / safe_name
    tmp = target.with_suffix(target.suffix + ".tmp")

    if tmp.exists():
        try:
            tmp.unlink()
        except Exception:
            pass

    request = urllib.request.Request(_encode_url(asset.download_url), headers={"User-Agent": USER_AGENT})

    with urllib.request.urlopen(request, timeout=45) as response:
        total = int(response.headers.get("content-length") or asset.size or 0)
        downloaded = 0
        started = time.time()

        with open(tmp, "wb") as output:
            while True:
                chunk = response.read(1024 * 256)
                if not chunk:
                    break

                output.write(chunk)
                downloaded += len(chunk)

                elapsed = max(time.time() - started, 0.001)
                speed = downloaded / elapsed
                progress_callback(downloaded, total, speed)

    if target.exists():
        target.unlink()
    tmp.replace(target)

    if target.stat().st_size <= 0:
        raise RuntimeError(f"Downloaded update is empty: {target}")

    return target


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 256), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_sha256_asset(release: ReleaseInfo, downloaded_path: Path) -> ReleaseAsset | None:
    target_names = {
        f"{downloaded_path.name}.sha256".lower(),
        f"{downloaded_path.name}.sha256.txt".lower(),
    }

    for asset in release.assets:
        if asset.name.lower() in target_names:
            return asset

    # Some release builders use a shared checksum file.
    for asset in release.assets:
        name = asset.name.lower()
        if name.endswith(".sha256") and "checksums" in name:
            return asset

    return None


def parse_sha256(text: str, filename: str) -> str | None:
    filename = filename.lower()

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        parts = stripped.split()
        candidates = [part for part in parts if re.fullmatch(r"[a-fA-F0-9]{64}", part)]
        if not candidates:
            continue

        if len(parts) == 1:
            return candidates[0].lower()

        if filename in stripped.lower() or len(parts) <= 2:
            return candidates[0].lower()

    return None


def verify_download_checksum(release: ReleaseInfo, downloaded_path: Path) -> str:
    actual = sha256_file(downloaded_path)
    sha_asset = find_sha256_asset(release, downloaded_path)

    if not sha_asset:
        return f"SHA256: {actual}\nChecksum asset: not found, local hash only"

    expected_text = _request_text(sha_asset.download_url, timeout=15)
    expected = parse_sha256(expected_text, downloaded_path.name)

    if not expected:
        raise RuntimeError(f"Не удалось прочитать SHA256 из {sha_asset.name}")

    if expected.lower() != actual.lower():
        raise RuntimeError(
            "SHA256 не совпал. Обновление не будет запущено.\n\n"
            f"Expected: {expected}\n"
            f"Actual:   {actual}"
        )

    return f"SHA256 verified: {actual}\nChecksum asset: {sha_asset.name}"


def open_release_page():
    webbrowser.open(GITHUB_LATEST_RELEASE_PAGE)


def open_website():
    webbrowser.open(f"https://{GITHUB_OWNER}.github.io/{GITHUB_REPO}/")


def open_downloaded_update(path: str | Path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(str(path))

    if os.name == "nt":
        os.startfile(str(path))  # noqa: S606
        return

    if sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
        return

    subprocess.Popen(["xdg-open", str(path)])


def create_update_notes(release: ReleaseInfo, downloaded_path: Path) -> Path:
    checksum_result = verify_download_checksum(release, downloaded_path)

    notes = UPDATES_DIR / "latest_update.txt"
    notes.write_text(
        f"Lylos Launcher update downloaded\n\n"
        f"Source: {release.source}\n"
        f"Repo: {release.repo}\n"
        f"Current version: {APP_VERSION}\n"
        f"Latest version: {release.version}\n"
        f"Asset: {downloaded_path.name}\n"
        f"{checksum_result}\n\n"
        f"File path:\n{downloaded_path}\n\n"
        "If this is an installer .exe, LL can close itself and launch it.\n"
        "If this is portable .zip, extract it over the old portable folder.\n",
        encoding="utf-8",
    )
    return notes


def create_update_launcher_script(
    downloaded_path: str | Path,
    silent: bool = True,
    cleanup_dir: str | Path | None = None,
) -> Path:
    """Create a helper script that starts installer after LL exits.

    If ``cleanup_dir`` is given, the helper removes stale ``*.exe`` and
    ``*.py`` files from that folder (old launcher binaries/sources) before
    starting the freshly downloaded installer. The downloaded installer itself
    is never removed.
    """

    downloaded_path = Path(downloaded_path).resolve()
    UPDATES_DIR.mkdir(parents=True, exist_ok=True)

    script = UPDATES_DIR / "run_sm_update.cmd"
    parent_pid = os.getpid()

    if os.name == "nt":
        installer_args = ""
        if silent:
            installer_args = " /SILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS"

        cleanup_lines = ""
        if cleanup_dir is not None:
            cdir = Path(cleanup_dir).resolve()
            if downloaded_path.parent != cdir and cdir.exists():
                cleanup_lines = (
                    f'if exist "{cdir}\\*.exe" del /q "{cdir}\\*.exe"\r\n'
                    f'if exist "{cdir}\\*.py" del /q "{cdir}\\*.py"\r\n'
                )

        script.write_text(
            "@echo off\r\n"
            "title Lylos Launcher Update\r\n"
            "echo Waiting for Lylos Launcher to close...\r\n"
            f"set SM_PARENT_PID={parent_pid}\r\n"
            "for /l %%i in (1,1,60) do (\r\n"
            "  tasklist /FI \"PID eq %SM_PARENT_PID%\" 2>nul | find \"%SM_PARENT_PID%\" >nul\r\n"
            "  if errorlevel 1 goto sm_closed\r\n"
            "  timeout /t 1 /nobreak >nul\r\n"
            ")\r\n"
            ":sm_closed\r\n"
            "timeout /t 1 /nobreak >nul\r\n"
            + cleanup_lines
            + f'start "" "{downloaded_path}"{installer_args}\r\n',
            encoding="utf-8",
        )
    else:
        script.write_text(
            "#!/usr/bin/env sh\n"
            "sleep 2\n"
            f'xdg-open "{downloaded_path}" >/dev/null 2>&1 &\n',
            encoding="utf-8",
        )
        try:
            script.chmod(0o755)
        except Exception:
            pass

    return script


def start_installer_after_exit(
    downloaded_path: str | Path,
    silent: bool = True,
    cleanup_dir: str | Path | None = None,
) -> Path:
    """Start downloaded setup installer through helper script.

    The caller should close the Qt application after this function returns.
    ``cleanup_dir`` (optional) makes the helper delete stale ``*.exe`` and
    ``*.py`` files there before launching the new installer.
    """

    downloaded_path = Path(downloaded_path)

    if not downloaded_path.exists():
        raise FileNotFoundError(str(downloaded_path))

    if not is_installer_path(downloaded_path):
        raise RuntimeError("Автообновление доступно только для Setup .exe. Portable ZIP нужно распаковывать вручную.")

    script = create_update_launcher_script(downloaded_path, silent=silent, cleanup_dir=cleanup_dir)

    if os.name == "nt":
        flags = 0
        try:
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        except Exception:
            flags = 0

        subprocess.Popen(
            ["cmd.exe", "/c", str(script)],
            creationflags=flags,
            close_fds=True,
        )
        return script

    subprocess.Popen([str(script)], close_fds=True)
    return script
