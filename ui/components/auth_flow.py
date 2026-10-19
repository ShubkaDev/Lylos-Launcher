"""Общий поток авторизации Ely.by: QThread-воркер и оверлей прогресса.

Используется и страницей «Аккаунт и персонаж», и диалогом добавления
аккаунта (ui/components/account_setup.py).
"""

from __future__ import annotations

import threading

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
)


class AuthLoginWorker(QThread):
    status = Signal(str)
    success = Signal(dict)
    failed = Signal(str, str)
    cancelled = Signal(str)

    def __init__(self, provider: str):
        super().__init__()
        self.provider = provider
        self._stop = threading.Event()

    def stop(self):
        """Request a graceful stop (e.g. user pressed Cancel in the overlay)."""
        self._stop.set()

    def run(self):
        import traceback

        try:
            if self.provider == "ely":
                from auth.ely_auth import ElyAuthService
                from auth import oauth_config
                from auth.oauth_callback_server import OAuthCallbackServer

                service = ElyAuthService()
                service.ensure_configured()

                # Быстрая проверка параметров: если ely.by их отклоняет,
                # сразу показываем понятную ошибку вместо 4-минутного таймаута.
                probe = service.probe_login_url()
                if probe.get("success") is False:
                    raise RuntimeError(service.describe_probe_failure(probe))

                try:
                    callback = OAuthCallbackServer(oauth_config.get_ely_redirect_uri(), timeout=240)
                except OSError as error:
                    raise RuntimeError(
                        "Не удалось запустить локальный сервер приёма ответа Ely.by.\n\n"
                        f"Причина: {error}\n\n"
                        "Порт 127.0.0.1:8089 занят — скорее всего уже открыт другой "
                        "экземпляр Lylos Launcher. Закрой все окна лаунчера и попробуй ещё раз."
                    ) from None
                callback.start()
                try:
                    self.status.emit("Открываю браузер Ely.by...")
                    service.open_login_page()

                    self.status.emit("Ожидаю подтверждение Ely.by в браузере...")
                    redirect_url = callback.wait(self._stop)
                except OAuthCancelled:
                    raise
                except TimeoutError:
                    raise RuntimeError(
                        "Не дождались возврата из браузера.\n\n"
                        "Если на странице Ely.by ошибка «Invalid request (null required)» —\n"
                        "приложение не зарегистрировано или Redirect URI не совпадает.\n\n"
                        f"Client ID:    {oauth_config.get_ely_client_id()}\n"
                        f"Redirect URI: {oauth_config.get_ely_redirect_uri()}\n\n"
                        "Проверь приложение на https://account.ely.by/dev/applications"
                    ) from None
                finally:
                    callback.close()

                self.status.emit("Получаю профиль Ely.by...")
                account = service.complete_login_from_redirect_url(redirect_url)
                self.success.emit(account)
                return

            if self.provider == "ely_device":
                import webbrowser

                from auth.ely_auth import ElyAuthService

                service = ElyAuthService()
                service.ensure_configured()

                self.status.emit("Запрашиваю код устройства у Ely.by...")
                device = service.start_device_login()

                verification_uri = device.get("verification_uri") or service.DEVICE_CODE_PAGE
                user_code = str(device.get("user_code") or "")

                self.status.emit(f"Код: {user_code}. Открой сайт и введи код...")
                webbrowser.open(verification_uri)

                self.status.emit("Ожидаю подтверждение на сайте Ely.by...")
                account = service.complete_device_login(device)
                self.success.emit(account)
                return

            raise RuntimeError("Unknown provider")
        except Exception as error:
            from auth.oauth_callback_server import OAuthCancelled

            if isinstance(error, OAuthCancelled):
                self.cancelled.emit(str(error))
            else:
                self.failed.emit(str(error), traceback.format_exc())


class AuthProgressDialog(QDialog):
    """Блокирующий оверлей входа: спиннер, живые статусы и текст ошибки."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в Ely.by")
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        title = QLabel("Подключение аккаунта Ely.by")
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: #F5F3FF;")
        layout.addWidget(title)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # busy-индикатор (спиннер)
        self.progress.setFixedHeight(8)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Подготовка...")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #94A3B8; font-size: 13px;")
        layout.addWidget(self.status_label)

        row = QHBoxLayout()
        row.addStretch(1)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setFixedWidth(120)
        row.addWidget(self.cancel_btn)
        layout.addLayout(row)

    def update_status(self, text: str):
        self.status_label.setText(str(text))

    def showEvent(self, event):
        super().showEvent(event)
        try:
            from ui.animations import fade_in

            fade_in(self, duration=200)
        except Exception:
            pass

    def show_error(self, text: str):
        self.status_label.setText(str(text))
        self.status_label.setStyleSheet("color: #FCA5A5; font-size: 13px;")
