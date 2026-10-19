"""Красивое окно предложения обновиться.

Показывает название, версию и описание обновления, взятые из release.json.
Никаких прямых ссылок на ZIP: окно только предлагает обновиться, а сам
архив скачивает и устанавливает LylosUpdater.exe.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.app_info import APP_VERSION

VIOLET = "#8B5CF6"
CYAN = "#22D3EE"
TEXT = "#E5E7EB"
MUTED = "#94A3B8"

DIALOG_STYLE = f"""
QDialog#UpdateDialog {{
    background-color: #0B0E1A;
}}
QLabel#UpdateHeading {{
    color: #F5F3FF;
    font-size: 22px;
    font-weight: 800;
    background: transparent;
}}
QLabel#UpdateName {{
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 700;
    background: transparent;
}}
QLabel#UpdateVersion {{
    color: #0F0A1C;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {VIOLET}, stop:1 {CYAN});
    border-radius: 10px;
    padding: 4px 12px;
    font-weight: 800;
    font-size: 12px;
}}
QLabel#UpdateMuted {{
    color: {MUTED};
    font-size: 12px;
    background: transparent;
}}
QLabel#UpdateBody {{
    color: {TEXT};
    font-size: 13px;
    background: transparent;
}}
QFrame#UpdateCard {{
    background-color: rgba(20, 25, 48, 0.72);
    border: 1px solid rgba(139, 92, 246, 0.22);
    border-radius: 16px;
}}
QScrollArea#UpdateScroll {{
    background: transparent;
    border: none;
}}
QScrollArea#UpdateScroll > QWidget > QWidget {{
    background: transparent;
}}
QPushButton#UpdatePrimary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {VIOLET}, stop:1 {CYAN});
    color: #0F0A1C;
    font-weight: 800;
    border: none;
    border-radius: 12px;
    padding: 12px 22px;
}}
QPushButton#UpdatePrimary:hover {{
    border: 1px solid #A5F3FC;
}}
QPushButton#UpdateSecondary {{
    background-color: rgba(10, 14, 28, 0.9);
    color: {TEXT};
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 12px;
    padding: 12px 20px;
}}
QPushButton#UpdateSecondary:hover {{
    border-color: {CYAN};
}}
"""


class UpdateDialog(QDialog):
    """Диалог «Доступно обновление» с названием, версией и описанием."""

    def __init__(self, release, parent=None):
        super().__init__(parent)
        self.setObjectName("UpdateDialog")
        self.setWindowTitle("Доступно обновление")
        try:
            from pathlib import Path

            from PySide6.QtGui import QIcon

            icon_path = Path(__file__).resolve().parents[2] / "assets" / "LL.ico"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass
        self.setMinimumWidth(520)
        self.setMaximumWidth(640)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setStyleSheet(DIALOG_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(14)

        heading = QLabel("Доступно обновление")
        heading.setObjectName("UpdateHeading")
        root.addWidget(heading)

        muted = QLabel(f"У вас установлена версия {APP_VERSION}")
        muted.setObjectName("UpdateMuted")
        root.addWidget(muted)

        card = QFrame()
        card.setObjectName("UpdateCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        name_label = QLabel(str(getattr(release, "name", "") or "Lylos Launcher"))
        name_label.setObjectName("UpdateName")
        name_label.setWordWrap(True)

        version_label = QLabel(f"Версия {getattr(release, 'version', '')}")
        version_label.setObjectName("UpdateVersion")

        top_row.addWidget(name_label, 1)
        top_row.addWidget(version_label, 0, Qt.AlignTop)
        card_layout.addLayout(top_row)

        description = str(getattr(release, "body", "") or "").strip()
        if not description:
            description = "Новая версия Lylos Launcher уже доступна. Обновитесь, чтобы получить все улучшения."

        body_label = QLabel(description)
        body_label.setObjectName("UpdateBody")
        body_label.setWordWrap(True)
        body_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        scroll = QScrollArea()
        scroll.setObjectName("UpdateScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setMaximumHeight(220)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addWidget(body_label)
        scroll_layout.addStretch(1)
        scroll.setWidget(scroll_content)

        card_layout.addWidget(scroll)
        root.addWidget(card, 1)

        hint = QLabel(
            "Обновление скачает и установит LylosUpdater, затем запустит лаунчер заново."
        )
        hint.setObjectName("UpdateMuted")
        hint.setWordWrap(True)
        root.addWidget(hint)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch(1)

        later_btn = QPushButton("Позже")
        later_btn.setObjectName("UpdateSecondary")
        later_btn.clicked.connect(self.reject)

        update_btn = QPushButton("Обновить сейчас")
        update_btn.setObjectName("UpdatePrimary")
        update_btn.setDefault(True)
        update_btn.clicked.connect(self.accept)

        buttons.addWidget(later_btn)
        buttons.addWidget(update_btn)
        root.addLayout(buttons)

    @classmethod
    def ask(cls, release, parent=None) -> bool:
        """Показать окно. Возвращает True, если пользователь выбрал «Обновить»."""
        dialog = cls(release, parent)
        return dialog.exec() == QDialog.Accepted

    def showEvent(self, event):
        super().showEvent(event)
        try:
            from ui.animations import fade_in

            fade_in(self, duration=200)
        except Exception:
            pass
