import logging
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QRect, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.icon_utils import icon

logger = logging.getLogger(__name__)


class ProfileAvatar(QWidget):
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedSize(30, 30)
        self.skin_path = None

    def set_skin(self, skin_path, _username):
        self.skin_path = skin_path
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#304236"))
        painter.drawRoundedRect(self.rect(), 8, 8)
        if self.skin_path and Path(self.skin_path).is_file():
            pixmap = QPixmap(str(self.skin_path))
            if not pixmap.isNull() and pixmap.width() >= 64 and pixmap.height() >= 32:
                scale = max(1, pixmap.width() // 64)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
                painter.drawPixmap(QRect(3, 3, 24, 24), pixmap,
                                   QRect(8 * scale, 8 * scale, 8 * scale, 8 * scale))
                return
        painter.drawPixmap(5, 5, icon("accounts").pixmap(QSize(20, 20)))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)


class AccountChip(QFrame):
    """Плашка аккаунта в выпадающем списке: аватар, ник, провайдер и кнопки.

    Кнопки:
      - «По умолчанию» — этот аккаунт станет активным (с ним запустится Minecraft);
      - «Настройки акк.» — открывает окно «Аккаунт и персонаж».
    """

    default_clicked = Signal(str)
    settings_clicked = Signal()

    def __init__(self, account: dict, is_active: bool, skin_path=None, parent=None):
        super().__init__(parent)
        self.account = account
        self.account_id = str(account.get("id") or "")
        self.setObjectName("AccountChipActive" if is_active else "AccountChip")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(10)

        from ui.components.skin_preview import SkinFaceWidget

        avatar = SkinFaceWidget(36)
        avatar.set_skin(skin_path, account.get("username", "OFF"))
        top.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(1)

        name = QLabel(str(account.get("display_name") or account.get("username") or "LLPlayer"))
        name.setObjectName("AccountChipName")
        info.addWidget(name)

        provider = str(account.get("provider") or "offline").lower()
        provider_text = "Ely.by" if provider in {"ely", "ely.by", "ely_by"} else "Offline"
        meta = QLabel(provider_text + (" • активен" if is_active else ""))
        meta.setObjectName("AccountChipMeta")
        info.addWidget(meta)

        top.addLayout(info, 1)
        layout.addLayout(top)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        buttons.addStretch(1)

        default_btn = QPushButton("✓ По умолчанию" if is_active else "По умолчанию")
        default_btn.setObjectName("SmallPrimaryButton" if not is_active else "SmallGhostButton")
        default_btn.setCursor(Qt.PointingHandCursor)
        default_btn.setFixedHeight(28)
        default_btn.setEnabled(not is_active)
        if not is_active:
            default_btn.clicked.connect(lambda: self.default_clicked.emit(self.account_id))
        buttons.addWidget(default_btn)

        settings_btn = QPushButton("Настройки акк.")
        settings_btn.setObjectName("SmallGhostButton")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setFixedHeight(28)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        buttons.addWidget(settings_btn)

        layout.addLayout(buttons)


class AccountDropdown(QFrame):
    """Выпадающий список аккаунтов (поповер над топбаром)."""

    account_selected = Signal(str)
    settings_requested = Signal()
    create_account_requested = Signal()

    POPUP_WIDTH = 330

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setObjectName("AccountDropdown")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)

        header = QLabel("Аккаунты")
        header.setObjectName("AccountDropdownTitle")
        outer.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.chips_layout = QVBoxLayout(self.container)
        self.chips_layout.setContentsMargins(0, 0, 0, 0)
        self.chips_layout.setSpacing(8)
        self.scroll.setWidget(self.container)
        outer.addWidget(self.scroll, 1)

        # Кнопка создания нового аккаунта — всегда внизу списка.
        self.create_account_btn = QPushButton("+ Создать аккаунт")
        self.create_account_btn.setObjectName("SmallPrimaryButton")
        self.create_account_btn.setCursor(Qt.PointingHandCursor)
        self.create_account_btn.setFixedHeight(32)
        self.create_account_btn.clicked.connect(self._on_create_account_clicked)
        outer.addWidget(self.create_account_btn)

        self.setFixedWidth(self.POPUP_WIDTH)

    def _on_create_account_clicked(self):
        self.close()
        self.create_account_requested.emit()

    def popup_below(self, anchor: QWidget):
        """Обновить список аккаунтов и показать поповер под anchor (кнопка топбара)."""
        self.refresh_chips()
        self.adjustSize()
        anchor_top = anchor.mapToGlobal(anchor.rect().topRight())
        self.move(anchor_top.x() - self.width(), anchor_top.y() + 8)
        self.show()

    def refresh_chips(self):
        from auth.account_manager import get_account_manager
        from core.skin_manager import SkinManager

        while self.chips_layout.count():
            item = self.chips_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        manager = get_account_manager()
        skins = SkinManager()
        accounts = manager.list_accounts()[:5]
        active = manager.get_active_account() or {}
        active_id = active.get("id")

        if not accounts:
            empty = QLabel("Пока нет аккаунтов")
            empty.setObjectName("AccountChipMeta")
            empty.setAlignment(Qt.AlignCenter)
            self.chips_layout.addWidget(empty)

        for account in accounts:
            skin = skins.get_account_skin(account)
            chip = AccountChip(account, account.get("id") == active_id, skin.get("path") if skin else None)
            chip.default_clicked.connect(self._on_default_clicked)
            chip.settings_clicked.connect(self._on_settings_clicked)
            self.chips_layout.addWidget(chip)

        self.chips_layout.addStretch(1)

        # Высота: до ~4 плашек, дальше — скролл.
        chip_height = 96
        visible = min(max(len(accounts), 1), 4)
        self.scroll.setFixedHeight(visible * chip_height + 8)
        self.adjustSize()

    def _on_default_clicked(self, account_id: str):
        self.close()
        self.account_selected.emit(account_id)

    def _on_settings_clicked(self):
        self.close()
        self.settings_requested.emit()


class Topbar(QWidget):
    """Global actions that should remain available on every page."""

    downloads_clicked = Signal()
    account_clicked = Signal()          # «Настройки акк.» — окно «Аккаунт и персонаж»
    theme_clicked = Signal()
    account_selected = Signal(str)      # выбран аккаунт «По умолчанию»
    create_account_requested = Signal() # «Создать аккаунт» в выпадающем списке

    THEME_LABELS = {
        "dark": "Тёмная", "amoled": "AMOLED", "forest": "Лес",
        "ocean": "Океан", "purple": "Эндер", "sunset": "Закат",
    }

    def __init__(self):
        super().__init__()
        self.setObjectName("Topbar")
        self.setFixedHeight(68)
        self.current_theme = "dark"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(10)

        self.title_label = QLabel("Главная")
        self.title_label.setObjectName("TopbarTitle")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.downloads_button = QPushButton("Загрузки")
        self.downloads_button.setObjectName("TopbarDownloadsButton")
        self.downloads_button.setIcon(icon("downloads"))
        self.downloads_button.setIconSize(QSize(17, 17))
        self.downloads_button.setCursor(Qt.PointingHandCursor)
        self.downloads_button.clicked.connect(self.downloads_clicked.emit)
        layout.addWidget(self.downloads_button)

        self.theme_button = QPushButton()
        self.theme_button.setObjectName("TopbarThemeButton")
        self.theme_button.setIcon(icon("settings"))
        self.theme_button.setIconSize(QSize(17, 17))
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.clicked.connect(self.theme_clicked.emit)
        self.theme_button.setFixedSize(36, 36)
        layout.addWidget(self.theme_button)

        self.account_button = QPushButton("LLPlayer")
        self.account_button.setObjectName("TopbarAccountButton")
        self.account_button.setCursor(Qt.PointingHandCursor)
        self.account_button.clicked.connect(self.toggle_account_dropdown)
        self.avatar = ProfileAvatar()
        self.avatar.setObjectName("TopbarAvatar")
        self.avatar.setCursor(Qt.PointingHandCursor)
        self.avatar.clicked.connect(self.toggle_account_dropdown)
        layout.addWidget(self.avatar)
        layout.addWidget(self.account_button)

        self.account_dropdown = AccountDropdown(self)
        self.account_dropdown.account_selected.connect(self.account_selected.emit)
        self.account_dropdown.settings_requested.connect(self.account_clicked.emit)
        self.account_dropdown.create_account_requested.connect(self.create_account_requested.emit)

        self.set_theme("dark")
        self.update_profile()

    # ---------- dropdown ----------

    def toggle_account_dropdown(self):
        if self.account_dropdown.isVisible():
            self.account_dropdown.close()
            return
        anchor = self.account_button if self.account_button.isVisible() else self.avatar
        self.account_dropdown.popup_below(anchor)

    def enterEvent(self, event):
        """Показывать аккаунты только при наведении на аватар или имя."""
        anchor = self.account_button if self.account_button.isVisible() else self.avatar
        over_account_control = self.account_button.underMouse() or self.avatar.underMouse()
        if over_account_control and not self.account_dropdown.isVisible():
            self.account_dropdown.popup_below(anchor)
        super().enterEvent(event)

    # ---------- обычные методы топбара ----------

    def set_page(self, title, subtitle=""):
        self.title_label.setText(title)
        self.title_label.setToolTip(subtitle)

    def set_compact(self, compact: bool):
        self.account_button.setVisible(not compact)

    def set_theme(self, theme: str | None):
        self.current_theme = str(theme or "dark").lower()
        label = self.THEME_LABELS.get(self.current_theme, "Тёмная")
        self.theme_button.setToolTip(f"Тема: {label}. Переключить")

    def set_download_count(self, count: int):
        count = max(0, int(count))
        self.downloads_button.setText(f"Загрузки · {count}" if count else "Загрузки")

    def update_profile(self):
        from auth.account_manager import AccountManager
        from core.skin_manager import SkinManager

        account = None
        skin_path = None
        try:
            account = AccountManager().get_active_account()
            if account:
                skin = SkinManager().get_account_skin(account)
                if skin:
                    skin_path = skin.get("path")
        except (OSError, ValueError, RuntimeError):
            logger.warning("Could not read account profile for topbar", exc_info=True)
        username = (account or {}).get("display_name") or (account or {}).get("username") or "LLPlayer"
        self.account_button.setText(username)
        self.account_button.setToolTip("Список аккаунтов (до 5)")
        self.avatar.set_skin(skin_path, username)
