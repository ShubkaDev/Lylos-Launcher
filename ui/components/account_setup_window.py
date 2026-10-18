"""Отдельное окно создания аккаунта с видео-фоном.

Показывается при первом запуске (если у пользователя ещё нет аккаунта)
ДО главного окна лаунчера — полностью отдельное окно, а не диалог
поверх главного меню.

Дизайн:
  - видео-фон на всё окно (QGraphicsView + QGraphicsVideoItem);
  - снизу красивый затемнённый прямоугольник с логотипом Lylos Launcher
    и тремя кнопками: «Звук», «Создать Offline аккаунт», «Создать Ely.by аккаунт»;
  - при нажатии на «Создать Offline аккаунт» прямоугольник плавно
    выезжает поверх видео и показывает форму ввода ника;
  - при нажатии на «Создать Ely.by аккаунт» прямоугольник так же выезжает
    и сразу показывает прогресс авторизации Ely.by.

ВАЖНО: видео рисуется через QGraphicsView + QGraphicsVideoItem, а НЕ через
QVideoWidget. На Windows QVideoWidget может рисоваться ПОВЕРХ остальных
виджетов окна (оверлей/кнопки становятся невидимыми, затемнение не видно).
QGraphicsVideoItem компонуется внутри сцены, поэтому элементы интерфейса
корректно рисуются поверх видео.

Видео берётся из ``assets/video-panarama/`` (рекомендуется MP4 H.264 + AAC).
Звук включён по умолчанию; кнопка «Звук» выключает/включает звук.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from PySide6.QtCore import QRectF, QSizeF, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from auth.account_manager import get_account_manager
from ui.components.auth_flow import AuthLoginWorker

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VIDEO_DIR = PROJECT_ROOT / "assets" / "video-panarama"

# Расширения, которые QtMultimedia (Windows Media Foundation) умеет открывать.
VIDEO_EXTENSIONS = (".mp4", ".webm", ".avi", ".mkv", ".mov", ".wmv", ".m4v", ".mpg", ".mpeg")

# Размеры панели (свёрнутая / развёрнутая).
PANEL_COLLAPSED_H = 270
PANEL_EXPANDED_H = 580
PANEL_MARGIN = 26

# Стили задаются прямо на виджетах, чтобы они применялись гарантированно
# (не зависели от каскада общих стилей).
_PANEL_SS = """
#SetupPanel {
    background-color: rgba(4, 8, 18, 0.92);
    border: 2px solid rgba(34, 211, 238, 0.55);
    border-radius: 26px;
}
#SetupPanel #SetupPanelTitle {
    color: #F4F6FF;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 4px;
}
#SetupPanel #SetupPanelSubtitle {
    color: #94A3B8;
    font-size: 13px;
    qproperty-wordWrap: true;
}
#SetupPanel QPushButton#SetupPanelButton {
    background-color: rgba(6, 11, 24, 0.96);
    border: 2px solid #22D3EE;
    border-radius: 16px;
    color: #F1F5F9;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 800;
}
#SetupPanel QPushButton#SetupPanelButton:hover {
    background-color: rgba(124, 58, 237, 0.40);
    border-color: #67E8F9;
}
#SetupPanel QPushButton#SetupPanelPrimaryButton {
    background-color: rgba(124, 58, 237, 0.55);
    border: 2px solid #22D3EE;
    border-radius: 16px;
    color: #FFFFFF;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 800;
}
#SetupPanel QPushButton#SetupPanelPrimaryButton:hover {
    background-color: rgba(124, 58, 237, 0.85);
    border-color: #67E8F9;
}
#SetupPanel QPushButton#SetupPanelGhostButton {
    background-color: rgba(6, 11, 24, 0.96);
    border: 1px solid rgba(148, 163, 184, 0.45);
    border-radius: 14px;
    color: #E2E8F0;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 700;
}
#SetupPanel QPushButton#SetupPanelGhostButton:hover {
    background-color: rgba(124, 58, 237, 0.30);
    border-color: rgba(34, 211, 238, 0.70);
}
#SetupPanel QLineEdit#SetupNickInput {
    background-color: rgba(10, 17, 32, 0.98);
    border: 2px solid rgba(34, 211, 238, 0.45);
    border-radius: 14px;
    color: #F1F5F9;
    padding: 12px 16px;
    font-size: 16px;
    font-weight: 700;
    selection-background-color: rgba(124, 58, 237, 0.6);
}
#SetupPanel QLabel#SetupSectionTitle {
    color: #E2E8F0;
    font-size: 16px;
    font-weight: 800;
    qproperty-wordWrap: true;
}
#SetupPanel QLabel#SetupMutedText {
    color: #94A3B8;
    font-size: 13px;
    qproperty-wordWrap: true;
}
#SetupPanel QLabel#SetupErrorText {
    color: #FCA5A5;
    font-size: 13px;
}
#SetupPanel QProgressBar {
    background-color: rgba(10, 17, 32, 0.9);
    border: none;
    border-radius: 4px;
    min-height: 8px;
    max-height: 8px;
    text-visible: false;
}
#SetupPanel QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B5CF6, stop:1 #22D3EE);
    border-radius: 4px;
}
"""


def find_background_video() -> Path | None:
    """Первый видеофайл в assets/video-panarama (или None, если видео нет)."""
    try:
        if not VIDEO_DIR.is_dir():
            return None
        for ext in VIDEO_EXTENSIONS:
            for path in sorted(VIDEO_DIR.glob(f"*{ext}")):
                if path.is_file():
                    return path
    except Exception:
        logger.debug("Video search failed", exc_info=True)
    return None


class AccountSetupWindow(QWidget):
    """Полноценное отдельное окно: видео на фоне + панель создания аккаунта."""

    account_created = Signal(dict)
    finished_setup = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("AccountSetupWindow")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("#AccountSetupWindow { background-color: #02040C; }")
        self.setWindowTitle("Lylos Launcher — создание аккаунта")
        self.setMinimumSize(980, 640)
        self.resize(1180, 720)

        try:
            icon_path = PROJECT_ROOT / "assets" / "LL.ico"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass

        self._player = None
        self._audio_output = None
        self._muted = False
        self.auth_worker: AuthLoginWorker | None = None

        # Анимация панели.
        self._panel_target = PANEL_COLLAPSED_H
        self._panel_timer = QTimer(self)
        self._panel_timer.setInterval(12)
        self._panel_timer.timeout.connect(self._panel_tick)

        self._build_ui()
        self._setup_video()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- видео-фон через QGraphicsView (корректный компоновщик) ---
        self.video_view = self._make_video_background()
        if self.video_view is not None:
            root.addWidget(self.video_view, 1)
        else:
            # Запасной тёмный фон, если QtMultimedia недоступен.
            fallback = QLabel("Lylos Launcher", self)
            fallback.setObjectName("SetupVideoBackground")
            fallback.setAlignment(Qt.AlignCenter)
            fallback.setStyleSheet(
                "#SetupVideoBackground { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                "stop:0 #0B0E1A, stop:0.5 #1E1445, stop:1 #083044); color: #F5F3FF; "
                "font-size: 42px; font-weight: 900; letter-spacing: 6px; }"
            )
            root.addWidget(fallback, 1)
            self.video_view = fallback

        # --- нижняя панель с логотипом и кнопками ---
        self.panel = QFrame(self)
        self.panel.setObjectName("SetupPanel")
        self.panel.setAttribute(Qt.WA_StyledBackground, True)
        self.panel.setStyleSheet(_PANEL_SS)
        self._build_panel_content()
        # Явно задаём высоту панели сразу, иначе до первого нажатия кнопки
        # self.panel.height() возвращает некорректное значение и панель
        # уезжает вниз / текст обрезается.
        self.panel.setFixedHeight(PANEL_COLLAPSED_H)

        self._layout_ui()

    def _build_panel_content(self):
        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(30, 16, 30, 18)
        layout.setSpacing(10)

        # --- логотип Lylos Launcher ---
        self.panel_title = QLabel("Lylos Launcher")
        self.panel_title.setObjectName("SetupPanelTitle")
        self.panel_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.panel_title)

        self.panel_subtitle = QLabel("Minecraft лаунчер для Windows")
        self.panel_subtitle.setObjectName("SetupPanelSubtitle")
        self.panel_subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.panel_subtitle)

        # --- три кнопки: звук, offline, ely.by ---
        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        self.mute_btn = QPushButton("🔊 Звук вкл")
        self.mute_btn.setObjectName("SetupPanelButton")
        self.mute_btn.setCursor(Qt.PointingHandCursor)
        self.mute_btn.setToolTip("Выключить/включить звук видео")
        self.mute_btn.clicked.connect(self.toggle_mute)
        buttons.addWidget(self.mute_btn)

        self.offline_btn = QPushButton("Создать Offline аккаунт")
        self.offline_btn.setObjectName("SetupPanelPrimaryButton")
        self.offline_btn.setCursor(Qt.PointingHandCursor)
        self.offline_btn.clicked.connect(self._on_offline_clicked)
        buttons.addWidget(self.offline_btn)

        self.ely_btn = QPushButton("Создать Ely.by аккаунт")
        self.ely_btn.setObjectName("SetupPanelPrimaryButton")
        self.ely_btn.setCursor(Qt.PointingHandCursor)
        self.ely_btn.clicked.connect(self._on_ely_clicked)
        buttons.addWidget(self.ely_btn)

        layout.addLayout(buttons)

        # --- содержимое, которое выезжает вместе с панелью ---
        self.panel_stack = QStackedWidget()
        layout.addWidget(self.panel_stack, 1)

        # Страница 0: пустая (только кнопки выше).
        self.panel_stack.addWidget(QWidget())

        # Страница 1: форма offline-ника.
        self.panel_stack.addWidget(self._build_offline_page())

        # Страница 2: прогресс Ely.by.
        self.panel_stack.addWidget(self._build_ely_page())

    def _build_offline_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(10)

        nick_label = QLabel("Никнейм персонажа")
        nick_label.setObjectName("SetupSectionTitle")
        page_layout.addWidget(nick_label)

        self.nick_input = QLineEdit()
        self.nick_input.setObjectName("SetupNickInput")
        self.nick_input.setPlaceholderText("Например, Steve")
        self.nick_input.setMaxLength(16)
        self.nick_input.returnPressed.connect(self._accept_offline)
        page_layout.addWidget(self.nick_input)

        nick_hint = QLabel("3–16 символов: a-z, A-Z, 0-9, _. Этот ник увидят сервера в offline-режиме.")
        nick_hint.setObjectName("SetupMutedText")
        nick_hint.setWordWrap(True)
        page_layout.addWidget(nick_hint)

        offline_buttons = QHBoxLayout()
        offline_buttons.setSpacing(10)
        back_offline = QPushButton("Назад")
        back_offline.setObjectName("SetupPanelGhostButton")
        back_offline.setCursor(Qt.PointingHandCursor)
        back_offline.clicked.connect(self._collapse_panel)
        offline_buttons.addWidget(back_offline)
        offline_buttons.addStretch(1)
        done_btn = QPushButton("Сохранить и продолжить")
        done_btn.setObjectName("SetupPanelPrimaryButton")
        done_btn.setCursor(Qt.PointingHandCursor)
        done_btn.clicked.connect(self._accept_offline)
        offline_buttons.addWidget(done_btn)
        page_layout.addLayout(offline_buttons)

        page_layout.addStretch(1)
        return page

    def _build_ely_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(10)

        ely_title = QLabel("Вход через Ely.by")
        ely_title.setObjectName("SetupSectionTitle")
        page_layout.addWidget(ely_title)

        self.ely_status = QLabel("Подготовка...")
        self.ely_status.setObjectName("SetupMutedText")
        self.ely_status.setWordWrap(True)
        page_layout.addWidget(self.ely_status)

        self.ely_progress = QProgressBar()
        self.ely_progress.setRange(0, 0)  # busy-индикатор
        self.ely_progress.setFixedHeight(8)
        page_layout.addWidget(self.ely_progress)

        ely_buttons = QHBoxLayout()
        ely_buttons.setSpacing(10)
        back_ely = QPushButton("Назад")
        back_ely.setObjectName("SetupPanelGhostButton")
        back_ely.setCursor(Qt.PointingHandCursor)
        back_ely.clicked.connect(self._cancel_ely_and_collapse)
        ely_buttons.addWidget(back_ely)
        ely_buttons.addStretch(1)
        self.ely_cancel_btn = QPushButton("Отмена")
        self.ely_cancel_btn.setObjectName("SetupPanelGhostButton")
        self.ely_cancel_btn.setCursor(Qt.PointingHandCursor)
        self.ely_cancel_btn.clicked.connect(self._cancel_ely_and_collapse)
        ely_buttons.addWidget(self.ely_cancel_btn)
        page_layout.addLayout(ely_buttons)

        page_layout.addStretch(1)
        return page

    def _make_video_background(self):
        """QGraphicsView с QGraphicsVideoItem — видео с корректным z-order."""
        try:
            from PySide6.QtMultimediaWidgets import QGraphicsVideoItem

            self.video_scene = QGraphicsScene(self)
            self.video_item = QGraphicsVideoItem()
            self.video_item.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)
            self.video_scene.addItem(self.video_item)

            view = QGraphicsView(self.video_scene)
            view.setObjectName("SetupVideoBackground")
            view.setFrameShape(QFrame.NoFrame)
            view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            view.setBackgroundBrush(QColor("#02040C"))
            view.setStyleSheet("QGraphicsView { background: #02040C; border: none; }")
            return view
        except Exception as error:
            logger.warning("QGraphicsVideoItem недоступен: %s", error)
            self.video_item = None
            return None

    def _layout_ui(self):
        """Позиционирование элементов и проверка z-order (сверху вниз обязательно)."""
        if hasattr(self, "panel"):
            panel_w = max(200, self.width() - PANEL_MARGIN * 2)
            # Высота панели: берём фактическую, но если она ещё не задана
            # (первый показ окна), используем целевую высоту.
            panel_h = self.panel.height()
            if panel_h < 120:
                panel_h = self._panel_target
            panel_h = max(120, min(self.height() - 40, panel_h))
            self.panel.setGeometry(
                PANEL_MARGIN,
                max(0, self.height() - panel_h - 18),
                panel_w,
                panel_h,
            )
        # UI поверх видео — явный порядок подъёма.
        for widget in (self.panel,):
            try:
                widget.raise_()
            except Exception:
                pass

        self._update_video_item()

    def _update_video_item(self):
        """Масштабировать кадр видео под размер окна (с обрезкой)."""
        item = getattr(self, "video_item", None)
        view = getattr(self, "video_view", None)
        if item is None or view is None:
            return
        try:
            rect = view.viewport().rect()
            self.video_item.setSize(QSizeF(rect.size()))
            view.setSceneRect(QRectF(rect))
        except Exception:
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self._layout_ui()
        # Повторная раскладка после того, как окно получит финальный размер.
        QTimer.singleShot(0, self._layout_ui)

    # ------------------------------------------------------------- animation
    def _animate_panel_to(self, target_height: int):
        self._panel_target = max(120, min(int(target_height), self.height() - 40))
        if not self._panel_timer.isActive():
            self._panel_timer.start()

    def _panel_tick(self):
        current = self.panel.height()
        target = self._panel_target
        diff = target - current
        if abs(diff) <= 4:
            self.panel.setFixedHeight(target)
            self._panel_timer.stop()
        else:
            self.panel.setFixedHeight(int(current + diff * 0.22))
        self._layout_ui()

    def _collapse_panel(self):
        self.panel_stack.setCurrentIndex(0)
        self._animate_panel_to(PANEL_COLLAPSED_H)

    # ------------------------------------------------------------- actions
    def _on_offline_clicked(self):
        self.panel_stack.setCurrentIndex(1)
        self._animate_panel_to(PANEL_EXPANDED_H)
        self.nick_input.setFocus()

    def _on_ely_clicked(self):
        self.panel_stack.setCurrentIndex(2)
        self._animate_panel_to(PANEL_EXPANDED_H)
        self._start_ely_auth()

    # ------------------------------------------------------------- offline
    def _accept_offline(self):
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

        if len(accounts) == 1:
            # Первый запуск: переименуем автоматический LLPlayer вместо создания второго.
            default_account = accounts[0]
            if (
                str(default_account.get("provider") or "offline").lower() == "offline"
                and str(default_account.get("username") or "").lower() == "llplayer"
            ):
                try:
                    account = manager.rename_account(default_account.get("id"), name)
                except Exception as error:
                    QMessageBox.warning(self, "Ошибка", str(error))
                    return
                self._finish(account)
                return

        account = manager.create_offline_account(name, make_active=True)
        self._finish(account)

    # ------------------------------------------------------------- ely.by
    def _start_ely_auth(self):
        from auth import oauth_config

        if not oauth_config.ely_is_configured():
            self.ely_status.setObjectName("SetupErrorText")
            self.ely_status.setStyleSheet(
                "#SetupErrorText { color: #FCA5A5; font-size: 13px; }"
            )
            self.ely_status.setText(
                "Ely.by не настроен.\n\n"
                "Задай ClientId/Secret через переменные окружения\n"
                "SM_ELY_CLIENT_ID / SM_ELY_CLIENT_SECRET\n"
                f"или в data/oauth_settings.json.\n\nRedirect URI: {oauth_config.get_ely_redirect_uri()}"
            )
            return

        if self.auth_worker and self.auth_worker.isRunning():
            return

        worker = AuthLoginWorker("ely")
        self.auth_worker = worker
        worker.status.connect(self._on_ely_status)
        worker.success.connect(self._on_ely_success)
        worker.failed.connect(self._on_ely_failed)
        worker.cancelled.connect(lambda _msg: self._on_ely_cancelled())
        worker.start()

    def _on_ely_status(self, text: str):
        self.ely_status.setObjectName("SetupMutedText")
        self.ely_status.setStyleSheet("#SetupMutedText { color: #94A3B8; font-size: 13px; }")
        self.ely_status.setText(str(text))

    def _on_ely_success(self, account: dict):
        if self.auth_worker is not None:
            self.auth_worker = None
        self._finish(account)

    def _on_ely_failed(self, error_text: str, _details: str):
        if self.auth_worker is not None:
            self.auth_worker = None
        self.ely_status.setObjectName("SetupErrorText")
        self.ely_status.setStyleSheet("#SetupErrorText { color: #FCA5A5; font-size: 13px; }")
        self.ely_status.setText(str(error_text))

    def _on_ely_cancelled(self):
        if self.auth_worker is not None:
            self.auth_worker = None
        self._collapse_panel()

    def _cancel_ely_and_collapse(self):
        if self.auth_worker and self.auth_worker.isRunning():
            self.auth_worker.stop()
        self.auth_worker = None
        self._collapse_panel()

    # ------------------------------------------------------------- finish
    def _finish(self, account: dict):
        self.account_created.emit(account)
        self.finished_setup.emit()
        self.close()

    # ---------------------------------------------------------------- video
    def _setup_video(self):
        item = getattr(self, "video_item", None)
        if item is None:
            logger.warning("Видео-выход недоступен — фон-заглушка.")
            self._fallback_background()
            return

        try:
            from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
        except Exception as error:
            logger.warning("QtMultimedia недоступен: %s", error)
            self._fallback_background()
            return

        video_path = find_background_video()
        if not video_path:
            logger.warning("Видео не найдено в assets/video-panarama — фон-заглушка.")
            self._fallback_background()
            return

        try:
            self._audio_output = QAudioOutput(self)
            self._audio_output.setVolume(0.8)
            self._player = QMediaPlayer(self)
            self._player.setAudioOutput(self._audio_output)
            self._player.setVideoOutput(item)
            self._player.setSource(QUrl.fromLocalFile(str(video_path)))
            self._player.setLoops(QMediaPlayer.Loops.Infinite)
            # Дополнительная гарантия зацикливания: если видео всё же
            # доходит до конца, сразу перезапускаем его.
            self._player.mediaStatusChanged.connect(self._on_media_status_changed)
            self._player.play()
        except Exception as error:
            logger.warning("Не удалось запустить видео: %s", error)
            self._fallback_background()

    def _fallback_background(self):
        """Если видео нет/не читается — статичная панорама под затемнением."""
        if not hasattr(self, "panel"):
            return
        try:
            from ui.splash import _pick_panorama

            path = _pick_panorama()
            if path:
                pix = QPixmap(str(path))
                if not pix.isNull():
                    label = QLabel(self)
                    label.setPixmap(
                        pix.scaled(
                            self.size(),
                            Qt.KeepAspectRatioByExpanding,
                            Qt.SmoothTransformation,
                        )
                    )
                    label.setGeometry(self.rect())
                    label.lower()
                    self._fallback_label = label
                    return
        except Exception:
            logger.debug("Panorama fallback failed", exc_info=True)

    def _on_media_status_changed(self, status):
        """Зацикливание видео (fallback к setLoops)."""
        try:
            if status == QMediaPlayer.MediaStatus.EndOfMedia and self._player is not None:
                self._player.play()
        except Exception:
            pass

    def toggle_mute(self):
        self._muted = not self._muted
        if self._audio_output is not None:
            self._audio_output.setMuted(self._muted)
        self.mute_btn.setText("🔇 Звук выкл" if self._muted else "🔊 Звук вкл")

    def closeEvent(self, event):
        if self._player is not None:
            try:
                self._player.stop()
            except Exception:
                pass
        if self.auth_worker and self.auth_worker.isRunning():
            self.auth_worker.stop()
        super().closeEvent(event)