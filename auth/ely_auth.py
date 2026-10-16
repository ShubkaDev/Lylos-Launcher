import base64
import hashlib
import logging
import os
import secrets
import tempfile
import time
import urllib.parse
import webbrowser

import requests

from auth import oauth_config
from auth.account_manager import get_account_manager
from core.constants import USER_AGENT


def _log_oauth_debug(line: str) -> None:
    try:
        with open(os.path.join(tempfile.gettempdir(), "sm_oauth_debug.log"), "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


logger = logging.getLogger(__name__)


class ElyAuthService:
    # Официальная документация Ely.by: эндпоинт авторизации — .../oauth2/v1.
    # См. https://docs.ely.by/en/oauth.html
    #
    # Тот же эндпоинт и формат ссылки использует Legacy Launcher:
    #   https://account.ely.by/oauth2/v1?client_id=...&response_type=code&scope=...&redirect_uri=...&state=...&prompt=select_account
    # Страница /oauth/choose-account, которую видно в Legacy Launcher, — это
    # промежуточный шаг выбора аккаунта, который сервер показывает при prompt=select_account.
    #
    # ВАЖНО про PKCE (code_challenge): сервер ely.by (League OAuth2 Server)
    # ТРЕБУЕТ code_challenge для публичных (desktop) клиентов. Без него возвращается
    # «Invalid request (null required)» — именно эту ошибку видели пользователи.
    # Поэтому здесь PKCE отправляется всегда (для confidential-клиентов он тоже допустим).
    #
    # ВАЖНО про срок жизни кода входа: ely.by выдаёт authorization_code на 10 минут
    # (PT10M в их AuthorizationServerFactory, исходники: github.com/elyby/accounts).
    # Код — stateless (зашифрованный JWT), «сгорает» только при успешном обмене.
    # Истёкший код при обмене даёт именно generic invalid_request — см.
    # exchange_code_for_token/_describe_exchange_failure.
    AUTH_URL = "https://account.ely.by/oauth2/v1"
    # API-эндпоинты ely.by живут под префиксом /api/...
    VALIDATE_URL = "https://account.ely.by/api/oauth2/v1/validate"
    TOKEN_URL = "https://account.ely.by/api/oauth2/v1/token"
    ACCOUNT_INFO_URL = "https://account.ely.by/api/account/v1/info"

    # OAuth2 Device Authorization Grant — вход без redirect_uri/callback.
    # Работает даже для desktop-приложений (у которых на ely.by нет Redirect URI).
    DEVICE_CODE_URL = "https://account.ely.by/api/oauth2/v1/devicecode"
    DEVICE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"
    DEVICE_CODE_PAGE = "https://account.ely.by/code"

    SCOPE_DEFAULT = "account_info account_email offline_access minecraft_server_session"

    SKIN_UPLOAD_PAGE = "https://ely.by/skins/add"
    PROFILE_PAGE = "https://ely.by/u/{username}"
    TOKEN_REFRESH_MARGIN_SECONDS = 120

    def __init__(self):
        self.state = None
        self.code_verifier = None

    @staticmethod
    def _pkce_challenge(code_verifier):
        digest = hashlib.sha256(str(code_verifier).encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    def ensure_configured(self):
        if not oauth_config.ely_is_configured():
            raise RuntimeError(
                "Ely.by OAuth не настроен.\n\n"
                "Нужно создать своё приложение на https://account.ely.by/dev/applications/new\n"
                "(тип «Website») с точным Redirect URI:\n"
                f"    {oauth_config.get_ely_redirect_uri()}\n\n"
                "Затем задай clientId (и при желании clientSecret) через переменные окружения\n"
                "SM_ELY_CLIENT_ID / SM_ELY_REDIRECT_URI\n"
                "или в data/oauth_settings.json: ely_client_id / ely_redirect_uri).\n\n"
                "Если страница Ely.by показывает «Invalid request (null required)» —\n"
                "значит client_id не найден или Redirect URI не совпадает с зарегистрированным."
            )

    def build_login_url(self):
        self.ensure_configured()

        self.state = secrets.token_urlsafe(24)
        # PKCE code_verifier: 43–128 символов [A-Za-z0-9-._~] по RFC-7636.
        self.code_verifier = secrets.token_urlsafe(48)

        # Тот же формат ссылки, что использует Legacy Launcher:
        #   /oauth2/v1?client_id=...&response_type=code&scope=...&redirect_uri=...&state=...&prompt=select_account
        # prompt=select_account заставляет сервер показать страницу выбора аккаунта
        # (/oauth/choose-account), после чего пользователь попадает в лаунчер с кодом.
        #
        # PKCE (code_challenge) обязателен для публичных desktop-клиентов ely.by,
        # иначе сервер отвечает «Invalid request (null required)».
        params = {
            "client_id": oauth_config.get_ely_client_id(),
            "response_type": "code",
            "scope": self.SCOPE_DEFAULT,
            "redirect_uri": oauth_config.get_ely_redirect_uri(),
            "state": self.state,
            "code_challenge": self._pkce_challenge(self.code_verifier),
            "code_challenge_method": "S256",
            "prompt": "select_account",
        }

        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def open_login_page(self):
        login_url = self.build_login_url()
        webbrowser.open(login_url)
        return login_url

    def probe_login_url(self, timeout: int = 15) -> dict:
        """Best-effort проверка параметров через /oauth2/v1/validate.

        Сервер отвечает JSON: {"success": true, ...} либо
        {"success": false, "error": ..., "parameter": ..., "statusCode": ...}.
        При сетевых проблемах возвращаем {"success": None}, чтобы не блокировать вход.
        """
        self.ensure_configured()

        # Публичным (desktop) клиентам ely.by обязательно нужен code_challenge,
        # поэтому и в проверке он передаётся (сгенерированный на лету).
        params = {
            "client_id": oauth_config.get_ely_client_id(),
            "redirect_uri": oauth_config.get_ely_redirect_uri(),
            "response_type": "code",
            "scope": self.SCOPE_DEFAULT,
            "state": "probe",
            "code_challenge": self._pkce_challenge(secrets.token_urlsafe(48)),
            "code_challenge_method": "S256",
        }

        try:
            response = requests.get(
                self.VALIDATE_URL,
                params=params,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
                timeout=timeout,
            )
            payload = response.json()
        except requests.RequestException as error:
            return {"success": None, "network_error": str(error)}
        except ValueError:
            return {"success": None, "network_error": "Сервер вернул не-JSON ответ"}

        if isinstance(payload, dict):
            return payload
        return {"success": None, "network_error": "Неожиданный ответ сервера"}

    def describe_probe_failure(self, probe: dict) -> str:
        """Человекочитаемое объяснение ошибки валидации Ely.by."""
        error = probe.get("error") or "unknown"
        parameter = probe.get("parameter")
        status_code = probe.get("statusCode") or ""

        lines = [
            "Ely.by отклонил параметры входа.",
            "",
            f"Ошибка: {error}" + (f" · параметр: {parameter}" if parameter else "") + (f" · HTTP {status_code}" if status_code else ""),
            "",
            "Это происходит, когда приложение не зарегистрировано на ely.by",
            "или Redirect URI не совпадает с тем, что указан в приложении.",
            "",
            "Что сделать:",
            "1. Открой https://account.ely.by/dev/applications/new",
            "2. Тип приложения: Website",
            f"3. Redirect URI укажи точно: {oauth_config.get_ely_redirect_uri()}",
            "4. Проверь, что ClientId в лаунчере совпадает с созданным приложением.",
        ]

        hint = probe.get("raw")
        if hint:
            lines.append("")
            lines.append(f"Ответ сервера: {hint}")
        elif probe.get("network_error"):
            lines.append("")
            lines.append(f"Сеть: {probe['network_error']}")

        return "\n".join(lines)

    @staticmethod
    def _parse_query(raw_query: str) -> dict[str, str]:
        """Разобрать query string, сохраняя литеральный '+' (RFC 3986).

        urllib.parse.parse_qs трактует '+' как пробел и тем самым портит
        значения (например, OAuth-коды), содержащие '+'. Здесь '+' остаётся
        плюсом, а %XX-последовательности декодируются корректно.
        """
        result: dict[str, str] = {}
        for pair in str(raw_query or "").split("&"):
            if not pair:
                continue
            if "=" in pair:
                key, value = pair.split("=", 1)
            else:
                key, value = pair, ""
            try:
                key = urllib.parse.unquote(key)
                value = urllib.parse.unquote(value)
            except Exception:
                pass
            if key and key not in result:
                result[key] = value
        return result

    def complete_login_from_redirect_url(self, redirect_url):
        self.ensure_configured()

        redirect_url = str(redirect_url or "").strip()

        if not redirect_url:
            raise RuntimeError("Вставь redirect URL после входа Ely.by.")

        parsed = urllib.parse.urlparse(redirect_url)
        query = self._parse_query(parsed.query)

        if "error" in query:
            error = query.get("error", "unknown")
            message = query.get("error_message", "Ошибка Ely.by OAuth")
            raise RuntimeError(f"{error}: {message}")

        code = query.get("code", "")
        state = query.get("state", "")

        if not code:
            raise RuntimeError("В redirect URL не найден параметр code.")

        if self.state and state != self.state:
            raise RuntimeError("OAuth state не совпал. Авторизация отменена.")

        token_data = self.exchange_code_for_token(code)
        user_info = self.get_user_info(token_data["access_token"])
        return self._save_ely_account(token_data, user_info)

    # ---------- OAuth2 Device Authorization Grant ----------

    def start_device_login(self, timeout: int = 25) -> dict:
        """Начать вход по коду устройства (как в Legacy Launcher / на Smart-TV).

        Этот способ не зависит от redirect_uri и callback-сервера —
        работает даже для desktop-приложений, у которых на ely.by нет Redirect URI.
        Возвращает: device_code, user_code, verification_uri, interval, expires_in.
        """
        self.ensure_configured()

        response = requests.post(
            self.DEVICE_CODE_URL,
            data={
                "client_id": oauth_config.get_ely_client_id(),
                "scope": self.SCOPE_DEFAULT,
            },
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
        )

        if response.status_code >= 400:
            raise RuntimeError(self._describe_error_response(response))

        data = response.json()
        if not data.get("device_code") or not data.get("user_code"):
            raise RuntimeError(f"Ely.by не вернул device_code/user_code: {data}")

        return data

    def poll_device_token(self, device_code: str, timeout: int = 25):
        """Опросить токен после подтверждения кода устройства.

        Пока пользователь не подтвердил код — возвращает None.
        """
        response = requests.post(
            self.TOKEN_URL,
            data=self._token_request_data({
                "grant_type": self.DEVICE_GRANT_TYPE,
                "device_code": device_code,
            }),
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
        )

        if response.status_code >= 400:
            try:
                payload = response.json()
            except Exception:
                payload = {}
            error = str(payload.get("error") or "").lower()
            if error in {"authorization_pending", "slow_down"}:
                return None
            if error in {"expired_token", "expired"}:
                raise RuntimeError("Код устройства истёк. Попробуй войти ещё раз.")
            raise RuntimeError(self._describe_error_response(response))

        data = response.json()
        if "access_token" not in data:
            raise RuntimeError(f"Ely.by не вернул access_token: {data}")
        return self._normalize_token_data(data)

    def complete_device_login(self, device_login: dict, max_wait_seconds: int = 300) -> dict:
        """Дождаться подтверждения кода устройства и получить профиль Ely.by."""
        device_code = str(device_login.get("device_code") or "")
        if not device_code:
            raise RuntimeError("Нет device_code для входа по коду устройства.")

        interval = max(1, int(device_login.get("interval") or 5))
        expires_in = int(device_login.get("expires_in") or 0)
        deadline = time.time() + (
            max_wait_seconds if expires_in <= 0 else min(max_wait_seconds, expires_in)
        )

        token_data = None
        while time.time() < deadline:
            token_data = self.poll_device_token(device_code)
            if token_data is not None:
                break
            time.sleep(interval)

        if token_data is None:
            raise RuntimeError("Время ожидания подтверждения истекло. Попробуй войти ещё раз.")

        user_info = self.get_user_info(token_data["access_token"])
        return self._save_ely_account(token_data, user_info)

    # ---------- общие помощники ----------

    def _save_ely_account(self, token_data: dict, user_info: dict) -> dict:
        """Сохранить аккаунт Ely.by и токены (общий код для всех способов входа)."""
        username = user_info.get("username")
        uuid = str(user_info.get("uuid", "")).replace("-", "")

        if not username:
            raise RuntimeError("Ely.by не вернул username.")

        manager = get_account_manager()

        account = {
            "type": "ely",
            "username": username,
            "display_name": username,
            "uuid": uuid,
            "provider": "ely",
            "access_token": token_data.get("access_token", ""),
            "refresh_token_saved": bool(token_data.get("refresh_token")),
            "profile_link": user_info.get("profileLink"),
            "email": user_info.get("email"),
        }

        saved = manager.upsert_account(account)
        manager.set_active_account(saved["id"])

        manager.save_tokens(
            saved["id"],
            {
                "access_token": token_data.get("access_token", ""),
                "refresh_token": token_data.get("refresh_token", ""),
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": token_data.get("expires_in", 0),
                "expires_at": token_data.get("expires_at", 0),
            },
        )

        # Сразу после входа скачиваем реальный скин Ely.by в локальную папку skins
        # и привязываем его к аккаунту — без этого в Vanilla персонаж выглядит как Steve.
        try:
            from core.skin_manager import SkinManager
            SkinManager().ensure_ely_skin(saved, force=True)
        except Exception:
            logger.debug("Ely.by skin download on login failed", exc_info=True)

        return saved

    @staticmethod
    def _describe_error_response(response) -> str:
        """Извлечь человекочитаемое описание ошибки из ответа Ely.by."""
        try:
            payload = response.json()
        except Exception:
            payload = {}

        error = payload.get("error") or payload.get("name") or ""
        message = (
            payload.get("message")
            or payload.get("error_description")
            or payload.get("errorMessage")
            or ""
        )

        if error or message:
            return f"{error}: {message}".strip(": ")
        return (response.text or f"HTTP {response.status_code}")[:500]

    def _token_request_data(self, extra):
        data = {
            "client_id": oauth_config.get_ely_client_id(),
            **dict(extra or {}),
        }

        client_secret = oauth_config.get_ely_client_secret()
        if client_secret:
            data["client_secret"] = client_secret

        return data

    def exchange_code_for_token(self, code):
        """Обменять код авторизации на access_token (https://docs.ely.by/en/oauth.html).

        Обязательные параметры по документации: client_id, client_secret,
        redirect_uri, grant_type=authorization_code, code. Дополнительно
        отправляется code_verifier (PKCE): публичным desktop-клиентам ely.by
        он нужен, а confidential-клиенты его игнорируют.

        ВАЖНО: код входа у ely.by живёт 10 минут (PT10M в их
        AuthorizationServerFactory) и «сгорает» только при УСПЕШНОМ обмене —
        коды там stateless (AuthCodeRepository::revokeAuthCode пустой).
        Поэтому при отказе обмена безопасна повторная попытка.

        Известная особенность сервера ely.by: он отвечает invalid_request
        на запрос с code_verifier, если код был выпущен без привязки к
        code_challenge (фронтенд ely.by при подтверждении входа пробрасывает
        только client_id/redirect_uri/response_type/scope/state — без
        code_challenge). Поэтому при неудаче первой попытки повторяем обмен
        без code_verifier.
        """
        base_data = self._token_request_data(
            {
                "redirect_uri": oauth_config.get_ely_redirect_uri(),
                "grant_type": "authorization_code",
                "code": str(code or ""),
            }
        )

        attempts = []
        if self.code_verifier:
            attempts.append(dict(base_data, code_verifier=self.code_verifier))
        attempts.append(base_data)

        last_response = None
        for attempt_index, data in enumerate(attempts):
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers={"User-Agent": USER_AGENT},
                timeout=25,
            )

            _log_oauth_debug(
                "TOKEN attempt=%d/%d code_len=%d verifier=%s client=%r redirect=%r secret=%s"
                % (
                    attempt_index + 1,
                    len(attempts),
                    len(str(code or "")),
                    "yes" if "code_verifier" in data else "no",
                    oauth_config.get_ely_client_id(),
                    oauth_config.get_ely_redirect_uri(),
                    "yes" if oauth_config.get_ely_client_secret() else "no",
                )
            )
            _log_oauth_debug("TOKEN_RESP %d %s" % (response.status_code, (response.text or "")[:500]))

            if response.status_code < 400:
                payload = response.json()

                if "access_token" not in payload:
                    raise RuntimeError(f"Ely.by не вернул access_token: {payload}")

                return self._normalize_token_data(payload)

            last_response = response
            if response.status_code != 400:
                # 401/5xx и т.п. — повторная попытка не поможет.
                break

        raise RuntimeError(self._describe_exchange_failure(last_response))

    def _describe_exchange_failure(self, response) -> str:
        """Человекочитаемое описание отказа при обмене кода на токен.

        Сервер ely.by возвращает невнятное generic-сообщение
        («The request is missing a required parameter...») сразу для
        нескольких разных причин. Расшифровываем их по error-коду:
          - invalid_request: чаще всего код входа истёк (TTL 10 минут) либо
            параметр не совпал с выданным кодом;
          - invalid_grant: код устарел/уже использован/не совпал;
          - invalid_client: не совпали client_id/client_secret/redirect_uri.
        """
        if response is None:
            return "Ely.by не ответил на обмен кода на токен."

        body = (response.text or "")[:400]
        try:
            payload = response.json()
        except Exception:
            payload = {}

        error = str(payload.get("error") or "")

        if error == "invalid_request":
            return (
                "Ely.by отклонил обмен кода на токен (invalid_request).\n\n"
                "Код входа у Ely.by живёт всего 10 минут. Если страница Ely.by\n"
                "была открыта заранее или вход занял много времени, код успевает\n"
                "устареть, и обмен отклоняется именно с такой ошибкой.\n\n"
                "Что делать: нажми «Войти через Ely.by» ещё раз и заверши вход\n"
                "на странице Ely.by без долгих пауз.\n\n"
                f"Ответ сервера: {body}"
            )

        if error == "invalid_grant":
            return (
                "Ely.by отклонил код входа (invalid_grant): код устарел, уже был\n"
                "использован или не совпал с параметрами входа.\n\n"
                "Что делать: нажми «Войти через Ely.by» ещё раз.\n\n"
                f"Ответ сервера: {body}"
            )

        if error == "invalid_client":
            return (
                "Ely.by не принял параметры приложения (invalid_client).\n\n"
                f"Client ID:    {oauth_config.get_ely_client_id()}\n"
                f"Redirect URI: {oauth_config.get_ely_redirect_uri()}\n\n"
                "Проверь приложение на https://account.ely.by/dev/applications\n"
                "(тип «Website», Redirect URI должен совпадать).\n\n"
                f"Ответ сервера: {body}"
            )

        return (
            f"Ely.by отклонил обмен кода на токен (HTTP {response.status_code}):\n{body}"
        )

    def _normalize_token_data(self, data, previous_refresh_token=""):
        normalized = dict(data or {})

        if not normalized.get("refresh_token") and previous_refresh_token:
            normalized["refresh_token"] = previous_refresh_token

        try:
            expires_in = int(normalized.get("expires_in") or 0)
        except (TypeError, ValueError):
            expires_in = 0

        normalized["expires_in"] = expires_in
        normalized["expires_at"] = int(time.time()) + expires_in if expires_in > 0 else 0
        normalized.setdefault("token_type", "Bearer")
        return normalized

    def refresh_access_token(self, account_id):
        self.ensure_configured()

        manager = get_account_manager()
        tokens = manager.load_tokens(account_id)
        refresh_token = tokens.get("refresh_token")

        if not refresh_token:
            raise RuntimeError("Для Ely.by аккаунта нет refresh_token. Войди в Ely.by заново.")

        # По документации ely.by в refresh-запросе передаётся тот же scope,
        # что был запрошен при входе (расширять список нельзя).
        response = requests.post(
            self.TOKEN_URL,
            data=self._token_request_data({
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": self.SCOPE_DEFAULT,
            }),
            headers={"User-Agent": USER_AGENT},
            timeout=25,
        )

        if response.status_code >= 400:
            raise RuntimeError(
                "Ely.by не обновил access_token: "
                f"{self._describe_error_response(response)}"
            )

        data = response.json()
        if "access_token" not in data:
            raise RuntimeError(f"Ely.by не обновил access_token: {data}")

        normalized = self._normalize_token_data(data, previous_refresh_token=refresh_token)
        manager.save_tokens(account_id, normalized)

        for account in manager.list_accounts():
            if account.get("id") == account_id:
                account["access_token"] = normalized.get("access_token", "")
                account["refresh_token_saved"] = bool(normalized.get("refresh_token"))
                manager.upsert_account(account)
                break

        return normalized

    def ensure_fresh_launch_token(self, account):
        if not account or str(account.get("provider") or "").lower() != "ely":
            return account

        account_id = account.get("id")
        if not account_id:
            return account

        manager = get_account_manager()
        tokens = manager.load_tokens(account_id)

        if not tokens:
            return account

        expires_at = int(tokens.get("expires_at") or 0)
        has_valid_token = bool(tokens.get("access_token")) and (
            not expires_at or expires_at - int(time.time()) > self.TOKEN_REFRESH_MARGIN_SECONDS
        )

        if has_valid_token:
            if account.get("access_token") != tokens.get("access_token"):
                account = dict(account)
                account["access_token"] = tokens.get("access_token", "")
                manager.upsert_account(account)
            return account

        refreshed = self.refresh_access_token(account_id)
        updated = dict(account)
        updated["access_token"] = refreshed.get("access_token", "")
        updated["refresh_token_saved"] = bool(refreshed.get("refresh_token"))
        return manager.upsert_account(updated)

    def get_user_info(self, access_token):
        response = requests.get(
            self.ACCOUNT_INFO_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=25,
        )

        if response.status_code >= 400:
            raise RuntimeError(response.text)

        return response.json()

    def open_skin_upload_page(self):
        webbrowser.open(self.SKIN_UPLOAD_PAGE)

    def open_profile_page(self, username):
        username = str(username or "").strip()

        if username:
            webbrowser.open(self.PROFILE_PAGE.format(username=username))
        else:
            webbrowser.open("https://ely.by")

    def get_skin_url(self, username):
        username = str(username or "").strip()
        return f"https://skinsystem.ely.by/skins/{username}.png"