from __future__ import annotations

import os
import tempfile
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer


# Страница-заглушка, на которую Ely.by перенаправляет после успешного обмена кода.
# Тот же адрес использует Legacy Launcher (appName=Legacy%20Launcher).
SUCCESS_PAGE_URL = "https://account.ely.by/oauth2/code/success?appName=SMLauncher"

# Диагностический лог OAuth (сырой callback + параметры обмена) — временный.
OAUTH_DEBUG_LOG = os.path.join(tempfile.gettempdir(), "sm_oauth_debug.log")


def log_oauth_debug(line: str) -> None:
    try:
        with open(OAUTH_DEBUG_LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


class OAuthCancelled(Exception):
    """Raised when the user cancels the OAuth wait."""


class OAuthCallbackServer:
    """Small one-shot localhost OAuth callback server for desktop launcher login."""

    def __init__(self, redirect_uri: str, timeout: int = 180):
        self.redirect_uri = str(redirect_uri)
        self.timeout = int(timeout or 180)
        parsed = urllib.parse.urlparse(self.redirect_uri)

        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        self.expected_path = parsed.path or "/"

        self.url = None
        self.error = None
        self._event = threading.Event()
        self._server = None
        self._thread = None

        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                log_oauth_debug(
                    "CALLBACK requestline=%r path=%r" % (self.requestline, self.path)
                )
                outer.url = f"http://{self.headers.get('Host')}{self.path}"

                parsed_request = urllib.parse.urlparse(self.path)
                # Толерантное сравнение пути: «/» и «» эквивалентны.
                expected = (outer.expected_path or "/").rstrip("/") or "/"
                requested = (parsed_request.path or "/").rstrip("/") or "/"
                ok = requested == expected

                if ok:
                    # Как в Legacy Launcher: браузер редиректится на страницу
                    # успеха ely.by, а код уже пойман локальным сервером.
                    self.send_response(302)
                    self.send_header("Location", SUCCESS_PAGE_URL)
                    body = b""
                else:
                    body = (
                        "<html><head><meta charset='utf-8'></head>"
                        "<body style='font-family:Segoe UI;background:#020617;color:#fecaca;padding:40px'>"
                        "<h1>Lylos Launcher</h1>"
                        "<p>Неверный callback path. Проверь redirect URI.</p>"
                        "</body></html>"
                    ).encode("utf-8")
                    self.send_response(404)
                    self.send_header("Content-Type", "text/html; charset=utf-8")

                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if body:
                    self.wfile.write(body)

                if ok:
                    outer._event.set()

            def log_message(self, format, *args):
                return

        self._server = HTTPServer((host, port), Handler)

    def start(self):
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def wait(self, stop_event=None):
        remaining = float(self.timeout)
        step = 0.5
        while remaining > 0:
            if stop_event is not None and stop_event.is_set():
                raise OAuthCancelled("Вход отменён пользователем.")
            if self._event.wait(min(remaining, step)):
                return self.url
            remaining -= step
        raise TimeoutError("Время ожидания OAuth callback истекло. Попробуй войти ещё раз.")

    def close(self):
        try:
            if self._server:
                self._server.shutdown()
                self._server.server_close()
        except Exception:
            pass
