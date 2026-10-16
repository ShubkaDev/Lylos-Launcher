import json
import os
import urllib.parse
from pathlib import Path

try:
    from storage.paths import DATA_DIR
except Exception:
    DATA_DIR = Path("data")


# Client ID задаётся локально перед сборкой или через настройки/переменные окружения.
# Для desktop-клиента используется PKCE; секрет не встраивается в приложение.
# Переопределить можно через SM_ELY_CLIENT_ID / SM_ELY_REDIRECT_URI
# или data/oauth_settings.json: ely_client_id / ely_redirect_uri.
try:
    from auth.oauth_config_local import ELY_CLIENT_ID as _LOCAL_ELY_CLIENT_ID
except ImportError:
    _LOCAL_ELY_CLIENT_ID = ""

DEFAULT_ELY_CLIENT_ID = _LOCAL_ELY_CLIENT_ID
# Redirect URI должен точно совпадать с зарегистрированным у Ely.by.
DEFAULT_ELY_REDIRECT_URI = "http://127.0.0.1:8089/"
OAUTH_SETTINGS_FILE = DATA_DIR / "oauth_settings.json"


def load_oauth_settings():
    try:
        if OAUTH_SETTINGS_FILE.exists():
            data = json.loads(OAUTH_SETTINGS_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def save_oauth_settings(data):
    if not isinstance(data, dict):
        data = {}
    OAUTH_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = OAUTH_SETTINGS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(OAUTH_SETTINGS_FILE)


def update_oauth_settings(**kwargs):
    data = load_oauth_settings()
    for key, value in kwargs.items():
        if value is None:
            continue
        data[key] = str(value).strip()
    save_oauth_settings(data)
    return data


def _setting_or_env(setting_key, env_keys, default=""):
    data = load_oauth_settings()
    if not isinstance(env_keys, (list, tuple)):
        env_keys = [env_keys]
    for env_key in env_keys:
        value = os.environ.get(env_key, "").strip()
        if value:
            return value
    return str(data.get(setting_key, default) or "").strip()


def get_ely_client_id():
    return _setting_or_env("ely_client_id", "SM_ELY_CLIENT_ID", DEFAULT_ELY_CLIENT_ID)


def get_ely_client_secret():
    return _setting_or_env(
        "ely_client_secret",
        "SM_ELY_CLIENT_SECRET",
        "",
    )


def get_ely_redirect_uri():
    value = _setting_or_env(
        "ely_redirect_uri",
        "SM_ELY_REDIRECT_URI",
        DEFAULT_ELY_REDIRECT_URI,
    )

    # Приложение smlauncher принимает redirect только на 127.0.0.1
    # (не localhost!) — проверено live. Если используем дефолтный клиент,
    # нормализуем хост, иначе ely.by вернёт invalid_client.
    if get_ely_client_id() == DEFAULT_ELY_CLIENT_ID:
        parsed = urllib.parse.urlparse(str(value))
        if parsed.hostname == "localhost":
            port = parsed.port or 80
            path = parsed.path or "/"
            return f"http://127.0.0.1:{port}{path}"
    return value


def ely_is_public_client():
    return not bool(get_ely_client_secret())


def ely_is_configured():
    return bool(get_ely_client_id() and get_ely_redirect_uri())


# Backward-compatible names for older code paths. New code should use getters above.
ELY_CLIENT_ID = get_ely_client_id()
ELY_CLIENT_SECRET = get_ely_client_secret()
ELY_REDIRECT_URI = get_ely_redirect_uri()
