from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from core.app_info import APP_DISPLAY_NAME
from core.constants import APP_VERSION


class AboutPage(QWidget):
    """Страница «О приложении»: описание лаунчера и ссылки разработчика."""

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(36, 32, 36, 32)
        root.setSpacing(18)

        title = QLabel("О приложении")
        title.setObjectName("PageTitle")

        subtitle = QLabel(f"{APP_DISPLAY_NAME} — открытый десктоп-лаунчер Minecraft.")
        subtitle.setObjectName("PageDescription")
        subtitle.setWordWrap(True)

        root.addWidget(title)
        root.addWidget(subtitle)

        app_card = QFrame()
        app_card.setObjectName("DownloadSummaryCard")
        app_layout = QVBoxLayout(app_card)
        app_layout.setContentsMargins(22, 20, 22, 20)
        app_layout.setSpacing(12)

        app_name = QLabel(f"{APP_DISPLAY_NAME} {APP_VERSION}")
        app_name.setObjectName("HeroTitle")

        app_about = QLabel(
            f"{APP_DISPLAY_NAME} — десктоп-лаунчер Minecraft, написанный на Python и PySide6 (Qt6). "
            "Позволяет создавать и запускать сборки (Vanilla, Fabric, Forge, NeoForge, Quilt), "
            "управлять модами, скинами, аккаунтами и обновлениями."
        )
        app_about.setObjectName("PanelText")
        app_about.setWordWrap(True)

        app_layout.addWidget(app_name)
        app_layout.addWidget(app_about)

        root.addWidget(app_card)

        dev_card = QFrame()
        dev_card.setObjectName("DownloadSummaryCard")
        dev_layout = QVBoxLayout(dev_card)
        dev_layout.setContentsMargins(22, 20, 22, 20)
        dev_layout.setSpacing(10)

        dev_title = QLabel("Разработчик")
        dev_title.setObjectName("HeroStatTitle")

        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(18)
        profile_text_layout = QVBoxLayout()
        profile_text_layout.setSpacing(8)

        dev_name = QLabel("ShubkaDev")
        dev_name.setObjectName("HeroTitle")
        dev_description = QLabel(
            "ShubkaDev — автор Lylos Launcher и разработчик проекта. "
            "Лаунчер развивается как открытый инструмент для создания и запуска "
            "Minecraft-сборок, работы с модами, аккаунтами и скинами."
        )
        dev_description.setObjectName("PanelText")
        dev_description.setWordWrap(True)
        profile_text_layout.addWidget(dev_name)
        profile_text_layout.addWidget(dev_description)
        profile_layout.addLayout(profile_text_layout, 1)

        skin_path = Path(__file__).resolve().parents[2] / "assets" / "Shubkadev-skin" / "skin.png"
        if skin_path.is_file():
            skin_pixmap = QPixmap(str(skin_path))
            if not skin_pixmap.isNull():
                skin_image = QLabel()
                skin_image.setObjectName("DeveloperSkinImage")
                skin_image.setAlignment(Qt.AlignCenter)
                skin_image.setPixmap(
                    skin_pixmap.scaled(
                        128,
                        128,
                        Qt.KeepAspectRatio,
                        Qt.FastTransformation,
                    )
                )
                skin_image.setToolTip("Скин ShubkaDev")
                profile_layout.addWidget(skin_image, 0, Qt.AlignTop)

        links = QLabel(
            '<a href="https://github.com/ShubkaDev/">GitHub: github.com/ShubkaDev</a><br>'
            '<a href="https://www.youtube.com/@shyb801_55">YouTube: @shyb801_55</a><br>'
            '<a href="https://gitflic.ru/project/shubkadev/lylos-launcher">GitFlic: проект Lylos Launcher</a>'
        )
        links.setOpenExternalLinks(True)
        links.setTextFormat(Qt.RichText)
        links.setObjectName("PanelText")

        dev_layout.addWidget(dev_title)
        dev_layout.addLayout(profile_layout)
        dev_layout.addWidget(links)

        root.addWidget(dev_card)
        root.addStretch()
