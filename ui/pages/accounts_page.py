from __future__ import annotations

import os
import threading
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QBoxLayout,
)

from auth.account_manager import AccountManager
from core.skin_manager import SkinError, SkinManager
from ui.components.auth_flow import AuthLoginWorker, AuthProgressDialog
from ui.components.skin_preview import Skin3DPreviewWidget, SkinFaceWidget
from ui.utils.helpers import clear_layout



class AccountsPage(QWidget):
    account_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.manager = AccountManager()
        self.skins = SkinManager()
        self.active_account = None
        self.active_skin = None
        self.auth_worker = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("ScrollArea")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        self.root_layout = QVBoxLayout(self.content_widget)
        self.root_layout.setContentsMargins(28, 22, 28, 18)
        self.root_layout.setSpacing(18)

        self.scroll.setWidget(self.content_widget)
        outer.addWidget(self.scroll)

        self.responsive_breakpoint = 980
        self.compact_breakpoint = 760

        self.build_ui()
        self.refresh_all()

    def build_ui(self):
        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title = QLabel("Аккаунт и персонаж")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "Скин, модель рук и настройки активного аккаунта. "
            "Добавить или выбрать аккаунт можно по нику в левом верхнем углу лаунчера."
        )
        subtitle.setObjectName("MutedText")
        subtitle.setWordWrap(True)

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.active_badge = QLabel("• OFFLINE")
        self.active_badge.setObjectName("StatusBadge")

        header.addLayout(title_box, 1)
        header.addWidget(self.active_badge, 0, Qt.AlignTop)

        self.root_layout.addLayout(header)

        self.skin_studio_panel = self.create_skin_studio_panel()
        self.root_layout.addWidget(self.skin_studio_panel)

        self.root_layout.addStretch(1)



    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_responsive_layout()

    def apply_responsive_layout(self):
        width = self.width()
        compact = width < self.compact_breakpoint
        narrow = width < self.responsive_breakpoint

        margins = (14, 14, 14, 14) if compact else (28, 22, 28, 18)
        self.root_layout.setContentsMargins(*margins)

        self.reflow_skin_action_buttons()

        if hasattr(self, "skin_studio_layout"):
            self.skin_studio_layout.setDirection(
                QBoxLayout.Direction.TopToBottom if narrow else QBoxLayout.Direction.LeftToRight
            )

    def reflow_skin_action_buttons(self):
        if not hasattr(self, "skin_buttons_grid"):
            return

        while self.skin_buttons_grid.count():
            item = self.skin_buttons_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        columns = 2 if self.width() < self.responsive_breakpoint else 3
        for index, button in enumerate(getattr(self, "skin_action_buttons", [])):
            self.skin_buttons_grid.addWidget(button, index // columns, index % columns)


    def reflow_stat_cards(self):
        if not hasattr(self, "stats_grid"):
            return

        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        columns = 1 if self.width() < self.compact_breakpoint else (2 if self.width() < self.responsive_breakpoint else 4)
        for index, card in enumerate(getattr(self, "stat_cards", [])):
            self.stats_grid.addWidget(card, index // columns, index % columns)

    def reflow_provider_cards(self):
        if not hasattr(self, "providers_grid"):
            return

        while self.providers_grid.count():
            item = self.providers_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        cards = [
            self.offline_provider_card,
            self.ely_provider_card,
        ]

        columns = 1 if self.width() < self.responsive_breakpoint else 3
        for index, card in enumerate(cards):
            self.providers_grid.addWidget(card, index // columns, index % columns)

    def create_stat_card(self, title, value, desc):
        card = QFrame()
        card.setObjectName("DownloadSummaryCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("HeroStatTitle")

        value_label = QLabel(value)
        value_label.setObjectName("DownloadBigNumber")

        desc_label = QLabel(desc)
        desc_label.setObjectName("InstanceMeta")

        card.value_label = value_label
        card.desc_label = desc_label

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        return card

    def create_skin_studio_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Card")

        layout = QHBoxLayout(panel)
        self.skin_studio_layout = layout
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(18)

        preview_box = QVBoxLayout()
        preview_box.setSpacing(10)
        self.preview = SkinFaceWidget(82)
        self.preview_3d = Skin3DPreviewWidget(190, 270)
        preview_box.addWidget(self.preview, 0, Qt.AlignHCenter)
        preview_box.addWidget(self.preview_3d, 0, Qt.AlignHCenter)
        layout.addLayout(preview_box)

        info = QVBoxLayout()
        info.setSpacing(8)

        self.skin_title = QLabel("Персонаж LLPlayer")
        self.skin_title.setObjectName("SectionTitle")

        self.skin_subtitle = QLabel("Скин не выбран. Загрузи PNG-скин Minecraft и привяжи его к активному профилю.")
        self.skin_subtitle.setObjectName("MutedText")
        self.skin_subtitle.setWordWrap(True)

        character_header = QHBoxLayout()
        character_header.setSpacing(8)
        character_header.addWidget(self.skin_title, 1)
        info.addLayout(character_header)

        info.addWidget(self.skin_subtitle)

        # --- Редактирование персонажа: имя + модель рук (сохраняется по кнопке) ---
        edit_box = QFrame()
        edit_box.setObjectName("Card")
        edit_inner = QVBoxLayout(edit_box)
        edit_inner.setContentsMargins(12, 10, 12, 10)
        edit_inner.setSpacing(8)

        edit_title = QLabel("Персонаж")
        edit_title.setObjectName("SmallSectionTitle")
        edit_inner.addWidget(edit_title)

        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        name_label = QLabel("Имя:")
        name_label.setObjectName("MutedText")
        self.person_name_edit = QLineEdit()
        self.person_name_edit.setObjectName("Input")
        self.person_name_edit.setPlaceholderText("Имя персонажа")
        name_row.addWidget(name_label)
        name_row.addWidget(self.person_name_edit, 1)
        edit_inner.addLayout(name_row)

        model_row = QHBoxLayout()
        model_row.setSpacing(8)
        model_label = QLabel("Модель рук:")
        model_label.setObjectName("MutedText")
        self.model_combo = QComboBox()
        self.model_combo.addItem("Авто", "auto")
        self.model_combo.addItem("Classic / Steve", "classic")
        self.model_combo.addItem("Slim / Alex", "slim")
        self.model_combo.setObjectName("Input")
        model_row.addWidget(model_label)
        model_row.addWidget(self.model_combo, 1)
        edit_inner.addLayout(model_row)

        self.save_character_btn = QPushButton("Сохранить персонажа")
        self.save_character_btn.setObjectName("PrimaryButton")
        self.save_character_btn.clicked.connect(self.save_character)
        edit_inner.addWidget(self.save_character_btn)

        info.addWidget(edit_box)

        # --- Редактирование аккаунта: заметка (сохраняется по кнопке) ---
        account_box = QFrame()
        account_box.setObjectName("Card")
        account_inner = QVBoxLayout(account_box)
        account_inner.setContentsMargins(12, 10, 12, 10)
        account_inner.setSpacing(8)

        account_title = QLabel("Аккаунт")
        account_title.setObjectName("SmallSectionTitle")
        account_inner.addWidget(account_title)

        note_label = QLabel("Заметка к аккаунту:")
        note_label.setObjectName("MutedText")
        self.account_note_edit = QLineEdit()
        self.account_note_edit.setObjectName("Input")
        self.account_note_edit.setPlaceholderText("Например: основная сборка, другое устройство")
        account_inner.addWidget(note_label)
        account_inner.addWidget(self.account_note_edit)

        self.save_account_btn = QPushButton("Сохранить аккаунт")
        self.save_account_btn.setObjectName("PrimaryButton")
        self.save_account_btn.clicked.connect(self.save_account_fields)
        account_inner.addWidget(self.save_account_btn)

        info.addWidget(account_box)

        # --- Кнопки работы со скинами и персонажем ---
        buttons = QGridLayout()
        buttons.setHorizontalSpacing(8)
        buttons.setVerticalSpacing(8)
        self.skin_buttons_grid = buttons

        upload_btn = QPushButton("+ Загрузить PNG-скин")
        upload_btn.setObjectName("PrimaryButton")
        upload_btn.clicked.connect(self.upload_skin)

        url_btn = QPushButton("Импорт по URL")
        url_btn.setObjectName("SecondaryButton")
        url_btn.clicked.connect(self.import_skin_url)

        ely_skin_btn = QPushButton("С Ely.by")
        ely_skin_btn.setObjectName("SecondaryButton")
        ely_skin_btn.clicked.connect(self.import_ely_skin)

        clear_btn = QPushButton("Убрать с профиля")
        clear_btn.setObjectName("SecondaryButton")
        clear_btn.clicked.connect(self.clear_active_skin)

        folder_btn = QPushButton("Папка skins")
        folder_btn.setObjectName("SecondaryButton")
        folder_btn.clicked.connect(self.open_skins_folder)

        rename_active_btn = QPushButton("Переименовать персонажа")
        rename_active_btn.setObjectName("SecondaryButton")
        rename_active_btn.clicked.connect(self.rename_active_character)

        delete_active_btn = QPushButton("Удалить персонажа")
        delete_active_btn.setObjectName("DangerButton")
        delete_active_btn.clicked.connect(self.delete_active_character)

        self.skin_action_buttons = [
            upload_btn,
            url_btn,
            ely_skin_btn,
            clear_btn,
            folder_btn,
            rename_active_btn,
            delete_active_btn,
        ]
        self.reflow_skin_action_buttons()
        info.addLayout(buttons)

        note = QLabel("Локальный PNG работает в сборках Fabric, Forge, NeoForge и Quilt, если для версии игры доступен CustomSkinLoader. Vanilla не поддерживает локальные скины. Другие игроки увидят скин только через Ely.by или свой мод скинов.")
        note.setObjectName("MutedText")
        note.setWordWrap(True)
        info.addWidget(note)

        layout.addLayout(info, 1)
        return panel

    def create_providers_panel(self) -> QWidget:
        wrap = QFrame()
        wrap.setObjectName("Card")

        layout = QGridLayout(wrap)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        self.providers_grid = layout

        self.offline_provider_card = self.provider_card(
            title="Offline профиль",
            badge="LOCAL",
            description="Локальный профиль для тестов и запуска без авторизации.",
            primary_text="+ Добавить Offline",
            secondary_text="Скопировать UUID",
            primary_action=self.add_offline_account,
            secondary_action=self.copy_active_uuid,
        )

        self.ely_provider_card = self.provider_card(
            title="Ely.by",
            badge="OAuth",
            description="Вход через Ely.by с поддержкой кастомных скинов.",
            primary_text="Войти через Ely.by",
            primary_action=self.login_ely,
            secondary_text="Вход по коду",
            secondary_action=self.login_ely_device,
        )

        self.reflow_provider_cards()
        return wrap

    def provider_card(self, title, badge, description, primary_text, primary_action, secondary_text=None, secondary_action=None):
        card = QFrame()
        card.setObjectName("MiniCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(9)

        top = QHBoxLayout()

        name = QLabel(title)
        name.setObjectName("CardTitle")

        badge_label = QLabel(badge)
        badge_label.setObjectName("SmallBadge")

        top.addWidget(name)
        top.addStretch(1)
        top.addWidget(badge_label)

        desc = QLabel(description)
        desc.setObjectName("MutedText")
        desc.setWordWrap(True)

        buttons = QHBoxLayout()

        primary = QPushButton(primary_text)
        primary.setObjectName("PrimaryButton")
        primary.clicked.connect(primary_action)

        buttons.addWidget(primary)

        if secondary_text and secondary_action:
            secondary = QPushButton(secondary_text)
            secondary.setObjectName("SecondaryButton")
            secondary.clicked.connect(secondary_action)
            buttons.addWidget(secondary)

        layout.addLayout(top)
        layout.addWidget(desc, 1)
        layout.addLayout(buttons)

        return card

    def create_accounts_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Card")
        panel.setMinimumWidth(0)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        top = QHBoxLayout()

        title = QLabel("Мои профили")
        title.setObjectName("SectionTitle")

        self.accounts_count = QLabel("0")
        self.accounts_count.setObjectName("MutedText")

        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(self.accounts_count)

        layout.addLayout(top)

        self.accounts_scroll = QScrollArea()
        self.accounts_scroll.setWidgetResizable(True)
        self.accounts_scroll.setFrameShape(QFrame.NoFrame)
        self.accounts_scroll.setMinimumHeight(156)

        self.accounts_container = QWidget()
        self.accounts_layout = QVBoxLayout(self.accounts_container)
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(10)

        self.accounts_scroll.setWidget(self.accounts_container)
        layout.addWidget(self.accounts_scroll, 1)

        return panel

    def create_skins_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Card")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        top = QHBoxLayout()

        title = QLabel("Библиотека скинов")
        title.setObjectName("SectionTitle")

        self.skins_count = QLabel("0")
        self.skins_count.setObjectName("MutedText")

        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(self.skins_count)

        layout.addLayout(top)

        self.skins_scroll = QScrollArea()
        self.skins_scroll.setWidgetResizable(True)
        self.skins_scroll.setFrameShape(QFrame.NoFrame)

        self.skins_container = QWidget()
        self.skins_grid = QGridLayout(self.skins_container)
        self.skins_grid.setContentsMargins(0, 0, 0, 0)
        self.skins_grid.setSpacing(12)

        self.skins_scroll.setWidget(self.skins_container)
        layout.addWidget(self.skins_scroll, 1)

        return panel

    def refresh_all(self):
        self.active_account = self.manager.get_active_account()
        self.active_skin = self.skins.get_account_skin(self.active_account)

        self.refresh_header()


    def refresh_account_stats(self):
        try:
            accounts = self.manager.list_accounts()
        except Exception:
            accounts = []

        try:
            skins = self.skins.list_skins()
        except Exception:
            skins = []

        account = self.active_account or {}
        provider = self.manager.format_provider(account.get("provider", "offline")).upper() if account else "OFFLINE"
        model = account.get("skin_model", "auto") if account else "auto"

        self.accounts_stat.value_label.setText(str(len(accounts)))
        self.skins_stat.value_label.setText(str(len(skins)))
        self.active_provider_stat.value_label.setText(provider)
        self.model_stat.value_label.setText(str(model).upper())

    def refresh_header(self):
        account = self.active_account

        if not account:
            self.preview.set_skin(None, "OFF")
            self.preview_3d.set_skin(None, "OFF")
            self.active_badge.setText("• OFFLINE")
            if hasattr(self, "person_name_edit"):
                self.person_name_edit.clear()
            if hasattr(self, "account_note_edit"):
                self.account_note_edit.clear()
            return

        username = account.get("username") or account.get("display_name") or "LLPlayer"
        provider = self.manager.format_provider(account.get("provider", "offline")).upper()

        self.active_badge.setText(f"• {provider}: {username}")

        if hasattr(self, "person_name_edit"):
            self.person_name_edit.setText(username)
        if hasattr(self, "account_note_edit"):
            self.account_note_edit.setText(str(account.get("note") or ""))

        if self.active_skin:
            self.preview.set_skin(self.active_skin.get("path"), username)
            self.preview_3d.set_skin(self.active_skin.get("path"), username)
            self.skin_title.setText(f"Персонаж {username}")

            model = account.get("skin_model") or self.active_skin.get("model", "auto")
            self.skin_subtitle.setText(
                f"Активный скин: {self.active_skin.get('name', 'Custom skin')} • "
                f"{self.active_skin.get('width', '?')}x{self.active_skin.get('height', '?')} • model: {model}"
            )

            idx = self.model_combo.findData(model)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
        else:
            self.preview.set_skin(None, username)
            self.preview_3d.set_skin(None, username)
            self.skin_title.setText(f"Персонаж {username}")
            self.skin_subtitle.setText("Скин не выбран. Загрузи PNG-скин Minecraft и привяжи его к активному профилю.")

    def refresh_accounts(self):
        clear_layout(self.accounts_layout)

        accounts = self.manager.list_accounts()
        active_id = self.active_account.get("id") if self.active_account else None

        self.accounts_count.setText(f"{len(accounts)} профилей")

        for account in accounts:
            self.accounts_layout.addWidget(self.account_row(account, active_id))

        self.accounts_layout.addStretch(1)

    def refresh_skins(self):
        clear_layout(self.skins_grid)

        skins = self.skins.list_skins()
        self.skins_count.setText(f"{len(skins)} скинов")

        if not skins:
            empty = QLabel("Скинов пока нет. Нажми «Загрузить PNG-скин» выше.")
            empty.setObjectName("MutedText")
            empty.setAlignment(Qt.AlignCenter)
            self.skins_grid.addWidget(empty, 0, 0)
            return

        columns = 1 if self.width() < self.responsive_breakpoint else 2
        for i, skin in enumerate(skins):
            self.skins_grid.addWidget(self.skin_card(skin), i // columns, i % columns)

    def account_row(self, account: dict, active_id: str | None) -> QWidget:
        row = QFrame()
        row.setObjectName("AccountRowActive" if account.get("id") == active_id else "AccountRow")
        row.setMinimumHeight(76)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 9, 10, 9)
        layout.setSpacing(10)

        skin = self.skins.get_account_skin(account)

        avatar = SkinFaceWidget(56)
        avatar.set_skin(skin.get("path") if skin else None, account.get("username", "OFF"))

        info = QVBoxLayout()

        name = QLabel(account.get("display_name") or account.get("username") or "LLPlayer")
        name.setObjectName("CardTitle")
        name.setWordWrap(False)

        meta = QLabel(self.manager.status_text(account))
        meta.setObjectName("MutedText")

        skin_text = QLabel("Скин: " + (skin.get("name") if skin else "не выбран"))
        skin_text.setObjectName("MutedText")

        info.addWidget(name)
        info.addWidget(meta)
        info.addWidget(skin_text)

        set_btn = QPushButton("Активировать")
        set_btn.setObjectName("SecondaryButton")
        if account.get("id") == active_id:
            set_btn.setText("✓ Активен")
            set_btn.setEnabled(False)
        else:
            set_btn.setEnabled(True)
        set_btn.clicked.connect(lambda checked=False, account_id=account.get("id"): self.set_active(account_id))

        rename_btn = QPushButton("Переименовать")
        rename_btn.setObjectName("SecondaryButton")
        rename_btn.clicked.connect(lambda checked=False, account_id=account.get("id"): self.rename_account(account_id))

        del_btn = QPushButton("Удалить")
        del_btn.setObjectName("DangerButton")
        del_btn.clicked.connect(lambda checked=False, account_id=account.get("id"): self.delete_account(account_id))
        del_btn.setVisible(len(self.manager.list_accounts()) > 1)

        # Кнопки в сетке 2×2: «Активировать» сверху на всю ширину,
        # «Переименовать» и «Удалить» снизу. Так они не вылезают за край.
        for action_btn in (set_btn, rename_btn, del_btn):
            action_btn.setMinimumWidth(118)
            action_btn.setCursor(Qt.PointingHandCursor)

        buttons = QGridLayout()
        buttons.setHorizontalSpacing(6)
        buttons.setVerticalSpacing(6)
        buttons.addWidget(set_btn, 0, 0, 1, 2)
        buttons.addWidget(rename_btn, 1, 0)
        buttons.addWidget(del_btn, 1, 1)

        layout.addWidget(avatar)
        layout.addLayout(info, 1)
        layout.addLayout(buttons)

        return row

    def rename_account(self, account_id):
        account = next((a for a in self.manager.list_accounts() if a.get("id") == account_id), None)
        if not account:
            return

        current = account.get("username") or account.get("display_name") or ""
        new_name, ok = QInputDialog.getText(
            self,
            "Переименовать персонажа",
            "Новое имя персонажа:",
            text=current,
        )
        if not ok:
            return

        new_name = str(new_name or "").strip()
        if not new_name:
            QMessageBox.warning(self, "Пустое имя", "Имя персонажа не может быть пустым.")
            return

        try:
            self.manager.rename_account(account_id, new_name)
        except Exception as error:
            QMessageBox.warning(self, "Не удалось переименовать", str(error))
            return

        active = self.manager.get_active_account()
        if active:
            self.account_changed.emit(active)
        self.refresh_all()

    def rename_active_character(self):
        account = self.active_account or self.manager.get_active_account()
        if not account:
            QMessageBox.information(self, "Нет персонажа", "Сначала добавь профиль.")
            return
        self.rename_account(account.get("id"))

    def save_character(self):
        """Сохранить изменения персонажа: имя и модель рук. Отдельная кнопка."""
        account = self.active_account or self.manager.get_active_account()
        if not account:
            QMessageBox.information(self, "Нет персонажа", "Сначала добавь профиль.")
            return
        account_id = account.get("id")

        new_name = str(self.person_name_edit.text() or "").strip()
        try:
            if new_name and new_name != (account.get("username") or account.get("display_name")):
                self.manager.rename_account(account_id, new_name)

            model = self.model_combo.currentData() or "auto"
            self.manager.set_account_model(account_id, model)
        except Exception as error:
            QMessageBox.warning(self, "Не удалось сохранить персонажа", str(error))
            self.refresh_all()
            return

        active = self.manager.get_active_account()
        if active:
            self.account_changed.emit(active)
        self.refresh_all()
        QMessageBox.information(self, "Персонаж сохранён", "Имя персонажа и модель рук обновлены.")

    def save_account_fields(self):
        """Сохранить изменения аккаунта: заметку. Отдельная кнопка."""
        account = self.active_account or self.manager.get_active_account()
        if not account:
            QMessageBox.information(self, "Нет аккаунта", "Сначала добавь профиль.")
            return

        note = str(self.account_note_edit.text() or "").strip()
        try:
            updated = self.manager.set_account_note(account.get("id"), note)
        except Exception as error:
            QMessageBox.warning(self, "Не удалось сохранить аккаунт", str(error))
            self.refresh_all()
            return

        if updated:
            self.account_changed.emit(updated)
        self.refresh_all()
        QMessageBox.information(self, "Аккаунт сохранён", "Заметка к аккаунту обновлена.")

    def delete_active_character(self):
        account = self.active_account or self.manager.get_active_account()
        if not account:
            return
        self.delete_account(account.get("id"))

    def skin_card(self, skin: dict) -> QWidget:
        card = QFrame()
        card.setObjectName("SkinCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        top = QHBoxLayout()

        preview = SkinFaceWidget(76)
        preview.set_skin(skin.get("path"), skin.get("name", "skin"))

        info = QVBoxLayout()

        name = QLabel(skin.get("name", "Custom skin"))
        name.setObjectName("CardTitle")

        meta = QLabel(f"{skin.get('width', '?')}x{skin.get('height', '?')} • {skin.get('model', 'auto')}")
        meta.setObjectName("MutedText")

        info.addWidget(name)
        info.addWidget(meta)

        top.addWidget(preview)
        top.addLayout(info, 1)

        layout.addLayout(top)

        buttons = QHBoxLayout()

        apply_btn = QPushButton("Применить")
        apply_btn.setObjectName("PrimaryButton")
        apply_btn.clicked.connect(lambda checked=False, skin_id=skin.get("id"): self.apply_skin(skin_id))

        open_btn = QPushButton("Файл")
        open_btn.setObjectName("SecondaryButton")
        open_btn.clicked.connect(lambda checked=False, path=skin.get("path"): self.open_file(path))

        delete_btn = QPushButton("Удалить")
        delete_btn.setObjectName("DangerButton")
        delete_btn.clicked.connect(lambda checked=False, skin_id=skin.get("id"): self.delete_skin(skin_id))

        buttons.addWidget(apply_btn)
        buttons.addWidget(open_btn)
        buttons.addWidget(delete_btn)

        layout.addLayout(buttons)

        return card

    def upload_skin(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите PNG-скин Minecraft",
            str(Path.home() / "Downloads"),
            "Minecraft skin (*.png);;PNG (*.png)",
        )

        if not file_path:
            return

        default_name = Path(file_path).stem
        name, ok = QInputDialog.getText(self, "Название скина", "Как назвать скин?", text=default_name)

        if not ok:
            return

        try:
            skin = self.skins.import_skin(
                file_path,
                name=name,
                model=self.model_combo.currentData() or "auto",
            )

            if self.active_account:
                self.skins.set_account_skin(
                    self.active_account.get("id"),
                    skin.get("id"),
                    self.model_combo.currentData() or "auto",
                )

            self.refresh_all()
            QMessageBox.information(self, "Скин загружен", "Скин привязан к активному профилю. Для отображения в игре запусти сборку Fabric, Forge, NeoForge или Quilt.")

        except SkinError as e:
            QMessageBox.warning(self, "Не удалось загрузить скин", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить скин:\n{e}")

    def _attach_imported_skin(self, skin, success_text: str):
        if self.active_account:
            account = self.skins.set_account_skin(
                self.active_account.get("id"),
                skin.get("id"),
                self.model_combo.currentData() or skin.get("model", "auto"),
            )
            self.account_changed.emit(account)
        self.refresh_all()
        QMessageBox.information(self, "Скин добавлен", success_text)

    def import_skin_url(self):
        url, ok = QInputDialog.getText(
            self,
            "Импорт скина по URL",
            "Вставь прямую ссылку на PNG-скин Minecraft:",
        )
        if not ok or not str(url or "").strip():
            return

        name, ok = QInputDialog.getText(self, "Название скина", "Как назвать скин?", text="URL skin")
        if not ok:
            return

        try:
            skin = self.skins.import_skin_from_url(
                str(url).strip(),
                name=name,
                model=self.model_combo.currentData() or "auto",
            )
            self._attach_imported_skin(skin, "Скин скачан по URL, добавлен в библиотеку и привязан к активному профилю.")
        except SkinError as e:
            QMessageBox.warning(self, "Не удалось импортировать скин", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать скин:\n{e}")

    def import_ely_skin(self):
        username = ""
        if self.active_account:
            username = self.active_account.get("username") or self.active_account.get("display_name") or ""
        username, ok = QInputDialog.getText(
            self,
            "Скин Ely.by",
            "Никнейм Ely.by / Minecraft:",
            text=username,
        )
        if not ok or not str(username or "").strip():
            return

        try:
            from auth.ely_auth import ElyAuthService

            url = ElyAuthService().get_skin_url(str(username).strip())
            skin = self.skins.import_skin_from_url(
                url,
                name=f"Ely.by {str(username).strip()}",
                model=self.model_combo.currentData() or "auto",
            )
            self._attach_imported_skin(skin, "Скин Ely.by загружен, добавлен в библиотеку и привязан к активному профилю.")
        except SkinError as e:
            QMessageBox.warning(self, "Не удалось загрузить Ely.by skin", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить Ely.by skin:\n{e}")

    def open_ely_skin_page(self):
        try:
            from auth.ely_auth import ElyAuthService

            username = ""
            if self.active_account:
                username = self.active_account.get("username") or self.active_account.get("display_name") or ""
            if username:
                ElyAuthService().open_profile_page(username)
            else:
                ElyAuthService().open_skin_upload_page()
        except Exception as e:
            QMessageBox.warning(self, "Ely.by", str(e))

    def apply_skin(self, skin_id: str):
        if not self.active_account:
            QMessageBox.warning(self, "Нет активного аккаунта", "Сначала создай или выбери профиль.")
            return

        try:
            account = self.skins.set_account_skin(
                self.active_account.get("id"),
                skin_id,
                self.model_combo.currentData() or "auto",
            )

            self.refresh_all()
            self.account_changed.emit(account)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def clear_active_skin(self):
        if not self.active_account:
            return

        account = self.skins.clear_account_skin(self.active_account.get("id"))
        self.refresh_all()

        if account:
            self.account_changed.emit(account)

    def delete_skin(self, skin_id: str):
        result = QMessageBox.question(
            self,
            "Удалить скин?",
            "Удалить скин из локальной библиотеки LL?",
        )

        if result != QMessageBox.Yes:
            return

        self.skins.delete_skin(skin_id)
        self.refresh_all()

    def open_skins_folder(self):
        path = str(self.skins.skins_dir)

        if os.name == "nt":
            os.startfile(path)
        else:
            import subprocess
            subprocess.Popen(["xdg-open", path])

    def open_file(self, path: str | None):
        if not path:
            return

        p = Path(path)

        if not p.exists():
            QMessageBox.warning(self, "Файл не найден", "Файл скина не найден.")
            return

        if os.name == "nt":
            os.startfile(str(p.parent))
        else:
            import subprocess
            subprocess.Popen(["xdg-open", str(p.parent)])

    def add_offline_account(self):
        while True:
            name, ok = QInputDialog.getText(self, "Offline профиль", "Введите никнейм (3-16 символов, a-z, 0-9, _):")

            if not ok:
                return

            name = name.strip()

            if not name:
                QMessageBox.warning(self, "Ошибка", "Никнейм не может быть пустым.")
                continue

            if len(name) < 3:
                QMessageBox.warning(self, "Ошибка", "Никнейм должен быть не короче 3 символов.")
                continue

            if len(name) > 16:
                QMessageBox.warning(self, "Ошибка", "Никнейм должен быть не длиннее 16 символов.")
                continue

            import re
            if not re.match(r"^[A-Za-z0-9_]+$", name):
                QMessageBox.warning(self, "Ошибка", "Никнейм может содержать только латинские буквы, цифры и нижнее подчёркивание.")
                continue

            account = self.manager.create_offline_account(name, make_active=True)
            self.refresh_all()
            self.account_changed.emit(account)
            return

    def set_active(self, account_id: str):
        account = self.manager.set_active_account(account_id)
        self.refresh_all()
        self.account_changed.emit(account)

    def start_auth_worker(self, provider: str):
        if self.auth_worker and self.auth_worker.isRunning():
            QMessageBox.information(self, "Вход уже идёт", "Дождись завершения текущего входа.")
            return

        worker = AuthLoginWorker(provider)
        self.auth_worker = worker

        overlay = AuthProgressDialog(self)
        worker.status.connect(lambda text: self.active_badge.setText(str(text)))
        worker.status.connect(overlay.update_status)
        worker.success.connect(lambda account: self.on_auth_success(worker, overlay, account))
        worker.failed.connect(lambda err, det: self.on_auth_failed(worker, overlay, err, det))
        worker.cancelled.connect(lambda msg: self.on_auth_cancelled(worker, overlay, msg))
        overlay.cancel_btn.clicked.connect(lambda: self._cancel_auth(worker, overlay))

        overlay.show()
        worker.start()
        # Блокирующий модальный цикл: обработчики сигналов сами закроют оверлей.
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
        # Любая ошибка обновления UI не должна ронять лаунчер после успешного входа.
        try:
            if account and account.get("provider") == "ely":
                self._try_import_ely_skin_for_account(account)

            self.refresh_all()
            active = self.manager.get_active_account()
            if active:
                self.account_changed.emit(active)
        except Exception:
            pass
        QMessageBox.information(self, "Вход выполнен", "Профиль подключён и активирован.")

    def on_auth_failed(self, worker: AuthLoginWorker, overlay: AuthProgressDialog, error_text: str, details: str):
        if self.auth_worker is not worker:
            return
        self.auth_worker = None
        try:
            overlay.show_error(str(error_text))
        except Exception:
            pass
        self.refresh_all()
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

    def on_auth_cancelled(self, worker: AuthLoginWorker, overlay: AuthProgressDialog, message: str):
        if self.auth_worker is not worker:
            return
        self.auth_worker = None
        try:
            overlay.close()
        except Exception:
            pass

    def _try_import_ely_skin_for_account(self, account: dict):
        """Загрузить скин Ely.by в фоне, чтобы GUI не зависал на сетевом запросе."""
        username = account.get("username") or account.get("display_name")
        account_id = account.get("id")
        if not username or not account_id:
            return

        def worker():
            try:
                from auth.ely_auth import ElyAuthService

                url = ElyAuthService().get_skin_url(username)
                skin = self.skins.import_skin_from_url(
                    url,
                    name=f"Ely.by {username}",
                    model=account.get("skin_model") or "auto",
                )
                self.skins.set_account_skin(
                    account_id,
                    skin.get("id"),
                    account.get("skin_model") or skin.get("model", "auto"),
                )
            except Exception:
                # У пользователя может ещё не быть скина на Ely.by. Вход всё равно успешен.
                pass

        threading.Thread(target=worker, daemon=True).start()

    def delete_account(self, account_id: str):
        accounts = self.manager.list_accounts()

        if len(accounts) <= 1:
            QMessageBox.information(self, "Нельзя удалить", "Должен остаться хотя бы один профиль.")
            return

        result = QMessageBox.question(
            self,
            "Удалить аккаунт?",
            "Удалить выбранный профиль из SMLauncher?",
        )

        if result != QMessageBox.Yes:
            return

        self.manager.delete_account(account_id)
        self.refresh_all()

        active = self.manager.get_active_account()
        if active:
            self.account_changed.emit(active)

    def copy_active_uuid(self):
        account = self.manager.get_active_account()

        if not account:
            return

        QApplication.clipboard().setText(str(account.get("uuid", "")))
        QMessageBox.information(self, "Скопировано", "UUID активного профиля скопирован.")

    def login_ely(self):
        from auth import oauth_config

        if not oauth_config.ely_is_configured():
            QMessageBox.warning(
                self,
                "Ely.by не настроен",
                "Для входа нужно приложение Ely.by.\n\n"
                "Задай ClientId/Secret через переменные окружения\n"
                "SM_ELY_CLIENT_ID / SM_ELY_CLIENT_SECRET\n"
                f"или в data/oauth_settings.json (ely_client_id, ely_client_secret).\n\n"
                f"Redirect URI: {oauth_config.get_ely_redirect_uri()}",
            )
            return

        self.start_auth_worker("ely")

    def login_ely_device(self):
        from auth import oauth_config

        if not oauth_config.ely_is_configured():
            QMessageBox.warning(
                self,
                "Ely.by не настроен",
                "Для входа по коду нужно приложение Ely.by.\n\n"
                "Задай ClientId через переменные окружения\n"
                "SM_ELY_CLIENT_ID\n"
                "или в data/oauth_settings.json (ely_client_id).\n\n"
                "«Вход по коду» не требует Redirect URI — код вводится на сайте ely.by.",
            )
            return

        self.start_auth_worker("ely_device")

    def ely_info(self):
        QMessageBox.information(
            self,
            "Ely.by",
            "Ely.by — бесплатная система скинов для Minecraft.\n\n"
            "После входа можно использовать кастомные скины в лаунчере."
        )

    def refresh(self):
        self.refresh_all()
