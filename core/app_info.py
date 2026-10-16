import os

APP_NAME = "SMLauncher"
APP_DISPLAY_NAME = "Lylos Launcher"
APP_VERSION = "1.0"
APP_CODENAME = "refresh"

APP_FULL_NAME = f"{APP_DISPLAY_NAME} {APP_VERSION}"
USER_AGENT = f"SMLauncher/{APP_VERSION}"

# Настрой под свой будущий GitHub repo перед первым релизом.
# Можно не менять код, а задать переменные окружения при сборке:
# SM_GITHUB_OWNER и SM_GITHUB_REPO.
GITHUB_OWNER = os.environ.get("SM_GITHUB_OWNER", "ShubkaDev")
GITHUB_REPO = os.environ.get("SM_GITHUB_REPO", "SMLauncher")
GITHUB_LATEST_RELEASE_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
GITHUB_LATEST_RELEASE_PAGE = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

WINDOWS_EXE_ASSET_PREFIX = "SMLauncher"
PORTABLE_ASSET_KEYWORD = "portable"

# Источник автообновлений публикуется на GitHub Pages.
WEBSITE_RELEASE_JSON_URL = os.environ.get(
    "SM_WEBSITE_RELEASE_JSON_URL",
    f"https://{GITHUB_OWNER}.github.io/{GITHUB_REPO}/release.json",
)
