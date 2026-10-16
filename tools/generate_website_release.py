from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEBSITE_DIR = ROOT / "website"


def read_app_version() -> str:
    text = (ROOT / "core" / "app_info.py").read_text(encoding="utf-8")
    match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', text)
    if not match:
        raise RuntimeError("APP_VERSION not found in core/app_info.py")
    return match.group(1)


def normalize_version(value: str | None) -> str:
    value = (value or "").strip()
    value = value.removeprefix("refs/tags/")
    value = value.removeprefix("v")
    return value or read_app_version()


def normalize_repo(value: str | None) -> str:
    value = (value or "").strip()
    if "/" in value:
        return value
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER") or "ShubkaDev"
    repo = os.environ.get("GITHUB_REPOSITORY", "").split("/")[-1] or "SMLauncher"
    return f"{owner}/{repo}"


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_index(version: str, repo: str):
    path = WEBSITE_DIR / "index.html"
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")

    display_version = version
    text = re.sub(r'(id="versionText">)[^<]+', rf"\g<1>{display_version}", text)
    text = re.sub(r'(id="versionStat">)[^<]+', rf"\g<1>{display_version}", text)
    text = re.sub(r'(id="footerVersion">)[^<]+', rf"\g<1>{display_version}", text)

    text = re.sub(
        r'SMLauncherSetup-\d+\.\d+\.\d+(?:\.\d+)?-win-x64\.exe',
        f"SMLauncherSetup-{version}-win-x64.exe",
        text,
    )
    text = re.sub(
        r'SMLauncher-\d+\.\d+\.\d+(?:\.\d+)?-win-x64-portable\.zip',
        f"SMLauncher-{version}-win-x64-portable.zip",
        text,
    )
    text = re.sub(r'window\.SM_VERSION\s*=\s*"[^"]+";', f'window.SM_VERSION = "{version}";', text)

    text = re.sub(
        r"<title>Lylos Launcher [^<]+</title>",
        f"<title>Lylos Launcher {version} — Minecraft лаунчер для Windows</title>",
        text,
    )
    text = re.sub(
        r'<meta name="description" content="Lylos Launcher [^"]+"',
        (
            f'<meta name="description" content="Lylos Launcher {version} — стабильный '
            "Minecraft-лаунчер для Windows. Сборки, моды, шейдеры, ресурспаки, Ely.by, "
            'installer и portable ZIP."'
        ),
        text,
    )
    text = re.sub(
        r'(<b id="releaseStatus">)[^<]+(</b>)',
        rf"\g<1>Стабильный релиз {version}\g<2>",
        text,
    )

    if "roadmap-item--current" in text:
        text = re.sub(
            r'(<article class="roadmap-item roadmap-item--current">\s*<time>)[^<]+(</time>)',
            rf"\g<1>v{version}\g<2>",
            text,
            count=1,
        )
        text = re.sub(
            r'(<article class="roadmap-item roadmap-item--current">[\s\S]*?<b>)[^<]+(</b>)',
            rf"\g<1>v{version} — новая главная и оболочка\g<2>",
            text,
            count=1,
        )
        text = re.sub(
            r'(<article class="roadmap-item roadmap-item--current">[\s\S]*?<p>)[^<]+(</p>)',
            r"\g<1>Главный экран для запуска активной сборки, компактная навигация и исправление установки Fabric.\g<2>",
            text,
            count=1,
        )

    if "window.SM_REPO" in text:
        text = re.sub(r'window\.SM_REPO\s*=\s*"[^"]+";', f'window.SM_REPO = "{repo}";', text)
    else:
        text = text.replace(
            f'window.SM_VERSION = "{version}";',
            f'window.SM_VERSION = "{version}";\n    window.SM_REPO = "{repo}";',
        )

    path.write_text(text, encoding="utf-8")


def patch_script(version: str, repo: str):
    path = WEBSITE_DIR / "script.js"
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'const repo\s*=\s*window\.SM_REPO\s*\|\|\s*"[^"]+";',
        f'const repo = window.SM_REPO || "{repo}";',
        text,
    )
    text = re.sub(
        r'const fallbackVersion\s*=\s*window\.SM_VERSION\s*\|\|\s*"[^"]+";',
        f'const fallbackVersion = window.SM_VERSION || "{version}";',
        text,
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=os.environ.get("SM_VERSION") or os.environ.get("GITHUB_REF_NAME"))
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    args = parser.parse_args()

    version = normalize_version(args.version)
    repo = normalize_repo(args.repo)
    base = f"https://github.com/{repo}/releases/latest/download"

    installer = f"SMLauncherSetup-{version}-win-x64.exe"
    portable = f"SMLauncher-{version}-win-x64-portable.zip"

    data = {
        "repo": repo,
        "version": version,
        "channel": "stable",
        "installer": f"{base}/{installer}",
        "portable": f"{base}/{portable}",
        "latest_release_api": f"https://api.github.com/repos/{repo}/releases/latest",
        "latest_release_page": f"https://github.com/{repo}/releases/latest",
        "direct_download": f"{base}/{installer}",
        "portable_download": f"{base}/{portable}",
        "installer_filename": installer,
        "portable_filename": portable,
        "platform": "windows-x64",
        "download_mode": "github-release-latest-download",
        "site_quality": "auto-deploy-latest-release",
    }

    write_json(
        WEBSITE_DIR / "release.json",
        {"version": version, "download_url": data["portable_download"]},
    )
    write_json(
        WEBSITE_DIR / "downloads" / "release.json",
        {
            "version": version,
            "channel": "stable",
            "repo": repo,
            "installer": data["installer"],
            "portable": data["portable"],
            "filename": installer,
            "download_url": data["direct_download"],
            "portable_filename": portable,
            "portable_download_url": data["portable_download"],
            "platform": "windows-x64",
            "source": "github-releases",
        },
    )

    # realese.json — источник версий для автообновления лаунчера.
    # Копия кладётся в корень репозитория и в website/ (публикуется на Pages).
    write_json(WEBSITE_DIR / "realese.json", data)
    write_json(ROOT / "realese.json", data)

    patch_index(version, repo)
    patch_script(version, repo)

    print(f"Generated website release metadata for {repo} v{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
