"""Создание аккаунта: Offline (ник) или Ely.by (OAuth).

Содержимое вынесено в ``AccountSetupContent`` — его используют:
  - диалог ``AddAccountDialog`` (старый путь «Добавить аккаунт»),
  - отдельное окно ``AccountSetupWindow`` с видео-фоном (первый запуск,
    когда у пользователя ещё нет аккаунта).
"""

from __future__ import annotations

import re

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from auth.account_manager import get_account_manager
from ui.components.auth_flow import AuthLoginWorker, AuthProgressDialog

MAX_ACCOUNTS = 5

NICK_HINT = "3–16 символов: a-z, A-Z, 0-9, _"


def accounts_capacity_reached() -> bool:
    return len(get_account_manager().list_accounts()) >= MAX_ACCOUNTS


class _ChoiceCard(QFrame):
    clicked = Signal()

    def __init__(self, title: str, badge: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("AccountChoiceCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(132)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        top = QHBoxLayout()
        name = QLabel(title)
        name.setObjectName("CardTitle")
        badge_label = QLabel(badge)
        badge_label.setObjectName("SmallBadge")
        top.addWidget(name)
        top.addStretch(1)
        top.addWidget(badge_label)
        layout.addLayout(top)

        desc = QLabel(description)
        desc.setObjectName("MutedText")
        desc.setWordWrap(True)
        layout.addWidget(desc, 1)
        layout.addStretch(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)


class AccountSetupContent(QWidget):
    """Вся логика создания аккаунта: выбор способа, offline-ник, Ely.by.

    Сигналы:
      account_created(dict) — аккаунт создан/подключён;
      skipped()             — пользователь решил пропустить (только onboarding).
    """

    account_created = Signal(dict)
    skipped = Signal()

    def __init__(self, parent=None, onboarding: bool = False):
        super().__init__(parent)
        self.onboarding = bool(onboarding)
        self.created_account: dict | None = None
        self.auth_worker: AuthLoginWorker | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(14)

        title = QLabel("Войди в аккаунт, чтобы играть" if self.onboarding else "Добавить аккаунт")
        title.setObjectName("PageTitle")
        root.addWidget(title)

        subtitle = QLabel(
            "Выбери способ входа. Можно играть без аккаунта (Offline) "
            "или войти через Ely.by — тогда скин и ник возьмутся из аккаунта."
        )
        subtitle.setObjectName("MutedText")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        # ---------- шаг 1: выбор способа ----------
        choice_page = QWidget()
        choice_layout = QVBoxLayout(choice_page)
        choice_layout.setContentsMargins(0, 0, 0, 0)
        choice_layout.setSpacing(12)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        offline_card = _ChoiceCard(
            "Создать Offline аккаунт",
            "LOCAL",
            "Играть без авторизации. Просто укажи ник — он сохранится и будет "
            "использоваться в Minecraft.",
        )
        offline_card.clicked.connect(self.show_offline_step)
        cards_row.addWidget(offline_card)

        ely_card = _ChoiceCard(
            "Создать Ely.by аккаунт",
            "OAUTH",
            "Войди через аккаунт Ely.by: откроется браузер, после входа профиль "
            "и скин подключатся автоматически.",
        )
        ely_card.clicked.connect(self.show_ely_step)
        cards_row.addWidget(ely_card)

        cards_row.addStretch(0)
        choice_layout.addLayout(cards_row)
        choice_layout.addStretch(1)

        skip_row = QHBoxLayout()
        skip_row.addStretch(1)
        if self.onboarding:
            skip_btn = QPushButton("Пропустить пока")
            skip_btn.setObjectName("GhostButton")
            skip_btn.setCursor(Qt.PointingHandCursor)
            skip_btn.clicked.connect(self.skipped.emit)
            skip_row.addWidget(skip_btn)
        root.addLayout(skip_row)

        self.stack.addWidget(choice_page)  # index 0

        # ---------- шаг 2: offline ник ----------
        offline_page = QWidget()
        offline_layout = QVBoxLayout(offline_page)
        offline_layout.setContentsMargins(0, 0, 0, 0)
        offline_layout.setSpacing(12)

        nick_label = QLabel("Никнейм персонажа")
        nick_label.setObjectName("SectionTitle")
        offline_layout.addWidget(nick_label)

        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Например, Steve")
        self.nick_input.setMaxLength(16)
        self.nick_input.returnPressed.connect(self.accept_offline)
        offline_layout.addWidget(self.nick_input)

        nick_hint = QLabel(NICK_HINT + ". Этот ник увидят сервера в offline-режиме.")
        nick_hint.setObjectName("MutedText")
        nick_hint.setWordWrap(True)
        offline_layout.addWidget(nick_hint)
        offline_layout.addStretch(1)

        offline_buttons = QHBoxLayout()
        back_offline = QPushButton("Назад")
        back_offline.setObjectName("SecondaryButton")
        back_offline.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        offline_buttons.addWidget(back_offline)
        offline_buttons.addStretch(1)
        done_btn = QPushButton("Сохранить и продолжить")
        done_btn.setObjectName("PrimaryButton")
        done_btn.setCursor(Qt.PointingHandCursor)
        done_btn.clicked.connect(self.accept_offline)
        offline_buttons.addWidget(done_btn)
        offline_layout.addLayout(offline_buttons)

        self.stack.addWidget(offline_page)  # index 1

        # ---------- шаг 2: ely.by ----------
        ely_page = QWidget()
        ely_layout = QVBoxLayout(ely_page)
        ely_layout.setContentsMargins(0, 0, 0, 0)
        ely_layout.setSpacing(12)

        ely_title = QLabel("Вход через Ely.by")
        ely_title.setObjectName("SectionTitle")
        ely_layout.addWidget(ely_title)

        ely_desc = QLabel(
            "После нажатия кнопки откроется браузер со страницей Ely.by. "
            "Авторизуйся там — лаунчер сам поймает ответ и подключит профиль. "
            "Заверши вход без долгих пауз: код входа действует 10 минут."
        )
        ely_desc.setObjectName("MutedText")
        ely_desc.setWordWrap(True)
        ely_layout.addWidget(ely_desc)
        ely_layout.addStretch(1)

        ely_buttons_grid = QGridLayout()
        ely_buttons_grid.setHorizontalSpacing(10)
        ely_buttons_grid.setVerticalSpacing(10)

        browser_btn = QPushButton("Войти через браузер")
        browser_btn.setObjectName("PrimaryButton")
        browser_btn.setCursor(Qt.PointingHandCursor)
        browser_btn.clicked.connect(self.login_ely_browser)
        ely_buttons_grid.addWidget(browser_btn, 0, 0)

        code_btn = QPushButton("Войти по коду устройства")
        code_btn.setObjectName("SecondaryButton")
        code_btn.setCursor(Qt.PointingHandCursor)
        code_btn.clicked.connect(self.login_ely_device)
        ely_buttons_grid.addWidget(code_btn, 0, 1)

        ely_layout.addLayout(ely_buttons_grid)

        ely_nav = QHBoxLayout()
        back_ely = QPushButton("Назад")
        back_ely.setObjectName("SecondaryButton")
        back_ely.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        ely_nav.addWidget(back_ely)
        ely_nav.addStretch(1)
        if self.onboarding:
            skip2 = QPushButton("Пропустить пока")
            skip2.setObjectName("GhostButton")
            skip2.clicked.connect(self.skipped.emit)
            ely_nav.addWidget(skip2)
        ely_layout.addLayout(ely_nav)

        self.stack.addWidget(ely_page)  # index 2

    # ---------- навигация ----------

    def show_offline_step(self):
        self.nick_input.setFocus()
        self.stack.setCurrentIndex(1)

    def show_ely_step(self):
        self.stack.setCurrentIndex(2)

    # ---------- offline ----------

    def accept_offline(self):
        name = str(self.nick_input.text() or "").strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Никнейм не может быть пустым.")
            return
        if len(name) < 3:
            QMessageBox.warning(self, "Ошибка", "Никнейм должен быть не короче 3 символов.")
            return
        if len(name) > 16:
            QMessageBox.warning(self, "Ошибка", "Никнейм должен быть не длиннее 16 символов.")
            return
        if not re.match(r"^[A-Za-z0-9_]+$", name):
            QMessageBox.warning(
                self,
                "Ошибка",
                "Никнейм может содержать только латинские буквы, цифры и нижнее подчёркивание.",
            )
            return

        manager = get_account_manager()
        accounts = manager.list_accounts()

        if self.onboarding and len(accounts) == 1:
            # Первый запуск: переименуем автоматический LLPlayer вместо создания второго.
            default_account = accounts[0]
            if (
                str(default_account.get("provider") or "offline").lower() == "offline"
                and str(default_account.get("username") or "").lower() == "llplayer"
            ):
                try:
                    self.created_account = manager.rename_account(default_account.get("id"), name)
                except Exception as error:
                    QMessageBox.warning(self, "Ошибка", str(error))
                    return
                self._finish(self.created_account)
                return

        if accounts_capacity_reached():
            QMessageBox.information(
                self,
                "Лимит аккаунтов",
                f"В лаунчере не может быть больше {MAX_ACCOUNTS} аккаунтов.\n"
                "Удали один из них в окне «Аккаунт и персонаж».",
            )
            return

        self.created_account = manager.create_offline_account(name, make_active=True)
        self._finish(self.created_account)

    # ---------- ely.by ----------

    def login_ely_browser(self):
        self.start_auth_worker("ely")

    def login_ely_device(self):
        self.start_auth_worker("ely_device")

    def start_auth_worker(self, provider: str):
        from auth import oauth_config

        if not oauth_config.ely_is_configured():
            QMessageBox.warning(
                self,
                "Ely.by не настроен",
                "Для входа нужно приложение Ely.by.\n\n"
                "Задай ClientId/Secret через переменные окружения\n"
                "SM_ELY_CLIENT_ID / SM_ELY_CLIENT_SECRET\n"
                "или в data/oauth_settings.json (ely_client_id, ely_client_secret).\n\n"
                f"Redirect URI: {oauth_config.get_ely_redirect_uri()}",
            )
            return

        if self.auth_worker and self.auth_worker.isRunning():
            QMessageBox.information(self, "Вход уже идёт", "Дождись завершения текущего входа.")
            return

        worker = AuthLoginWorker(provider)
        self.auth_worker = worker

        overlay = AuthProgressDialog(self)
        worker.status.connect(overlay.update_status)
        worker.success.connect(lambda account: self.on_auth_success(worker, overlay, account))
        worker.failed.connect(lambda err, det: self.on_auth_failed(worker, overlay, err, det))
        worker.cancelled.connect(lambda _msg: self.on_auth_cancelled(worker, overlay))
        overlay.cancel_btn.clicked.connect(lambda: self._cancel_auth(worker, overlay))

        overlay.show()
        worker.start()
        overlay.exec()

    def _cancel_auth(self, worker: AuthLoginWorker, overlay: AuthProgressDialog):
        worker.stop()
        try:
            overlay.close()
        except Exception:
            pass

    def on_auth_success(self, worker: AuthLoginWorker, overlay: AuthProgressDialog, account: dict):
        if self.auth_worker is not worker:
            return
        self.auth_worker = None
        try:
            overlay.close()
        except Exception:
            pass
        self.created_account = account
        self._finish(account)

    def on_auth_failed(self, worker: AuthLoginWorker, overlay: AuthProgressDialog, error_text: str, details: str):
        if self.auth_worker is not worker:
            return
        self.auth_worker = None
        try:
            overlay.show_error(str(error_text))
        except Exception:
            pass
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("Вход не выполнен")
        box.setText(str(error_text))
        box.setDetailedText(str(details))
        box.exec()
        try:
            overlay.close()
        except Exception:
            pass

    def on_auth_cancelled(self, worker: AuthLoginWorker, overlay: AuthProgressDialog, _message: str):
        if self.auth_worker is not worker:
            return
        self.auth_worker = None
        try:
            overlay.close()
        except Exception:
            pass

    # ---------- завершение ----------

    def _finish(self, account: dict):
        self.created_account = account
        self.account_created.emit(account)


class AddAccountDialog(QDialog):
    """Окно добавления аккаунта (модальный диалог поверх главного окна).

    onboarding=True — окно показывается при первом запуске: тогда у него
    заголовок приветствия и кнопка «Пропустить».
    """

    account_created = Signal(dict)

    def __init__(self, parent=None, onboarding: bool = False):
        super().__init__(parent)
        self.onboarding = bool(onboarding)
        self.created_account: dict | None = None
        self.auth_worker: AuthLoginWorker | None = None

        self.setWindowTitle("Добро пожаловать в SMLauncher" if self.onboarding else "Добавить аккаунт")
        self.setModal(True)
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.content = AccountSetupContent(self, onboarding=onboarding)
        self.content.account_created.connect(self._on_account_created)
        self.content.skipped.connect(self.reject)
        layout.addWidget(self.content)

    def _on_account_created(self, account: dict):
        self.created_account = account
        self.account_created.emit(account)
        self.accept()

    def closeEvent(self, event):
        if self.content.auth_worker and self.content.auth_worker.isRunning():
            self.content.auth_worker.stop()
        super().closeEvent(event)
