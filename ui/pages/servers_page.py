"""Страница «Сервера»: топ Minecraft-серверов, статусы и онлайны.

Работает как каталог: загрузка из сети с анимацией, поиск, сортировка,
карточки с кнопками «Копировать адрес» и «Открыть страницу».
"""

from __future__ import annotations

import time
import traceback

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.servers_catalog import fetch_top_servers
from ui.components.loading_widget import LoadingAnimation
from ui.utils.helpers import clear_layout

ONLINE_GREEN = "#22C55E"
OFFLINE_GRAY = "#475569"


def _fmt_number(value) -> str:
    try:
        value = int(value or 0)
    except (TypeError, ValueError):
        return "0"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f} млн"
    if value >= 1_000:
        return f"{value / 1_000:.1f} тыс".replace(".0", "")
    return str(value)


class ServerListWorker(QThread):
    success = Signal(object)
    failed = Signal(str, str)

    def __init__(self, limit: int = 100, parent=None):
        super().__init__(parent)
        self.limit = limit

    def run(self):
        try:
            servers = fetch_top_servers(limit=self.limit)
            self.success.emit(servers or [])
        except Exception as error:
            self.failed.emit(str(error), traceback.format_exc())


class ServersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.servers: list[dict] = []
        self.filtered: list[dict] = []
        self.loading_widget = None
        self.worker = None
        self.busy = False
        self._did_autoload = False
        self._last_load_time = 0.0
        self._last_columns = 0

        self.build_ui()

    # ── UI ──────────────────────────────────────────────────────────────
    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(8)

        # Верхняя строка: описание + кнопка обновления
        header = QHBoxLayout()
        header.setSpacing(8)

        title = QLabel("Топ-серверы")
        title.setObjectName("SectionTitle")
        header.addWidget(title)
        header.addStretch()

        self.refresh_button = QPushButton("⟳ Обновить")
        self.refresh_button.setObjectName("PrimaryButton")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setFixedHeight(34)
        self.refresh_button.clicked.connect(lambda: self.start_load(force=True))
        header.addWidget(self.refresh_button)
        root.addLayout(header)

        # Статистика
        stats = QGridLayout()
        stats.setHorizontalSpacing(8)
        stats.setVerticalSpacing(8)
        self.total_stat = self.create_stat_card("Серверов", "—", "в списке")
        self.online_stat = self.create_stat_card("Онлайн", "—", "сейчас доступно")
        self.players_stat = self.create_stat_card("Игроков", "—", "суммарно онлайн")
        for idx, card in enumerate([self.total_stat, self.online_stat, self.players_stat]):
            stats.addWidget(card, 0, idx)
        stats.setColumnStretch(3, 1)
        root.addLayout(stats)

        # Панель управления: поиск + сортировка
        controls = QHBoxLayout()
        controls.setSpacing(8)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("поиск по названию или адресу…")
        self.query_input.setClearButtonEnabled(True)
        self.query_input.textChanged.connect(self.apply_filter)
        self.query_input.setMinimumWidth(180)
        controls.addWidget(self.query_input, 1)

        self.sort_combo = QComboBox()
        self.sort_combo.setMinimumWidth(150)
        self.sort_combo.addItem("По онлайну", "players")
        self.sort_combo.addItem("По названию", "name")
        self.sort_combo.currentIndexChanged.connect(self.apply_filter)
        controls.addWidget(self.sort_combo)

        self.count_label = QLabel("")
        self.count_label.setObjectName("CompactStatus")
        self.count_label.setFixedHeight(34)
        controls.addWidget(self.count_label)

        root.addLayout(controls)

        # Статус
        self.status_label = QLabel("Загрузка топ-серверов…")
        self.status_label.setObjectName("PanelText")

        # Сетка результатов
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setObjectName("ScrollArea")

        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(2, 2, 2, 2)
        self.grid.setHorizontalSpacing(14)
        self.grid.setVerticalSpacing(14)
        self.scroll.setWidget(self.container)

        hint = QLabel("Статусы и онлайны обновляются автоматически • Источник: LL-каталог серверов • Живые статусы: mcsrvstat.us")
        hint.setObjectName("MutedText")
        hint.setWordWrap(True)

        root.addWidget(self.status_label)
        root.addWidget(self.scroll, 1)
        root.addWidget(hint)

    def create_stat_card(self, title, value, desc):
        card = QFrame()
        card.setObjectName("DownloadSummaryCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
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

    # ── Жизненный цикл ──────────────────────────────────────────────────
    def showEvent(self, event):
        super().showEvent(event)
        if not self._did_autoload:
            self._did_autoload = True
            QTimer.singleShot(200, lambda: self.start_load(force=True))

    def refresh_on_show(self):
        """Вызывается из главного окна: обновляет список, если данные устарели."""
        if self.busy:
            return
        if time.time() - self._last_load_time > 300:
            self.start_load(force=True)

    def start_load(self, force=False):
        if self.busy:
            return
        if not force and self.servers:
            self.render_results()
            return

        self.busy = True
        self.refresh_button.setEnabled(False)
        self.status_label.setText("Загрузка списка серверов…")
        self._begin_loading()

        self.worker = ServerListWorker(limit=100)
        self.worker.success.connect(self.on_success)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    # ── Загрузка и отображение ──────────────────────────────────────────
    def on_success(self, servers):
        self.busy = False
        self.refresh_button.setEnabled(True)
        self._last_load_time = time.time()
        self.servers = list(servers or [])
        self.status_label.setText(f"Загружено {len(self.servers)} серверов • обновление каждые 5 минут")
        self.render_results()

    def on_failed(self, error_text, details):
        self.busy = False
        self.refresh_button.setEnabled(True)
        self.status_label.setText("Ошибка загрузки серверов.")
        self._stop_loading()
        self._show_load_error(error_text, str(details))

    def _begin_loading(self):
        clear_layout(self.grid)
        self._stop_loading()
        widget = LoadingAnimation(text_prefix="Загрузка серверов", subtitle="Собираем топ по онлайну…")
        self.loading_widget = widget
        self.grid.addWidget(widget, 0, 0, 1, 2)

    def _stop_loading(self):
        widget = getattr(self, "loading_widget", None)
        if widget is None:
            return
        try:
            widget.stop_animation()
        except Exception:
            pass
        widget.deleteLater()
        self.loading_widget = None

    def _show_load_error(self, error_text, details=""):
        clear_layout(self.grid)
        self._stop_loading()

        panel = QFrame()
        panel.setMinimumHeight(190)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("⚠️  Сервера не загрузились")
        title.setObjectName("PanelTitle")
        title.setAlignment(Qt.AlignCenter)

        message = QLabel(str(error_text)[:220])
        message.setObjectName("PanelText")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        retry = QPushButton("Повторить")
        retry.setCursor(Qt.PointingHandCursor)
        retry.setMinimumWidth(150)
        retry.clicked.connect(lambda: self.start_load(force=True))
        buttons.addWidget(retry)

        if details:
            more = QPushButton("Подробнее")
            more.setCursor(Qt.PointingHandCursor)
            more.setMinimumWidth(150)

            def show_details():
                box = QMessageBox(self)
                box.setIcon(QMessageBox.Critical)
                box.setWindowTitle("Ошибка серверов")
                box.setText("Не удалось загрузить список серверов.")
                box.setInformativeText(str(error_text))
                box.setDetailedText(str(details))
                box.exec()

            more.clicked.connect(show_details)
            buttons.addWidget(more)

        layout.addWidget(title)
        layout.addWidget(message)
        layout.addItem(buttons)

        self.grid.addWidget(panel, 0, 0, 1, 2)

    # ── Фильтр, сортировка, рендер ──────────────────────────────────────
    def apply_filter(self, *args):
        self.render_results()

    def responsive_columns(self):
        try:
            width = self.scroll.viewport().width()
        except Exception:
            width = self.width()
        return 2 if width >= 1200 else 1

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "grid") and self.servers:
            columns = self.responsive_columns()
            if columns != getattr(self, "_last_columns", 0):
                self.render_results()

    def render_results(self):
        self._stop_loading()
        clear_layout(self.grid)

        query = self.query_input.text().strip().lower()
        sort_key = self.sort_combo.currentData() or "players"

        filtered = []
        for server in self.servers:
            name = str(server.get("name") or "").lower()
            host = str(server.get("host") or server.get("address") or "").lower()
            if not query or query in name or query in host:
                filtered.append(server)

        if sort_key == "name":
            filtered.sort(key=lambda s: str(s.get("name") or "").lower())
        else:
            filtered.sort(key=lambda s: s.get("players", 0), reverse=True)

        self.filtered = filtered
        self.count_label.setText(f"{len(filtered)} / {len(self.servers)}")

        if not filtered:
            empty = QLabel(
                "Ничего не найдено. Попробуй изменить запрос."
                if query
                else "Список серверов пока пуст. Нажми «Обновить»."
            )
            empty.setObjectName("PanelText")
            empty.setAlignment(Qt.AlignCenter)
            empty.setMinimumHeight(140)
            self.grid.addWidget(empty, 0, 0, 1, 2)
            return

        columns = self.responsive_columns()
        self._last_columns = columns

        for index, server in enumerate(filtered):
            row = index // columns
            col = index % columns
            self.grid.addWidget(self.create_server_card(server), row, col)

        self.grid.setRowStretch((len(filtered) // columns) + 1, 1)

    # ── Карточка сервера ────────────────────────────────────────────────
    def create_server_card(self, server):
        card = QFrame()
        card.setObjectName("ModResultCard")
        card.setMinimumHeight(140)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        online = bool(server.get("online"))
        players = int(server.get("players") or 0)
        max_players = int(server.get("max_players") or 0)

        # Верхняя строка: статус + имя | игроки
        top = QHBoxLayout()
        top.setSpacing(8)

        dot = QLabel("●")
        dot.setFixedWidth(16)
        dot.setStyleSheet(
            f"color:{ONLINE_GREEN}; font-size:16px;"
            if online
            else f"color:{OFFLINE_GRAY}; font-size:16px;"
        )
        dot.setToolTip("Онлайн" if online else "Оффлайн")

        name = QLabel(str(server.get("name") or "Minecraft Server"))
        name.setObjectName("InstanceTitle")
        name.setWordWrap(True)
        top.addWidget(dot, 0, Qt.AlignTop)
        top.addWidget(name, 1)

        players_badge = QLabel(f"👥 {_fmt_number(players)}" + (f" / {_fmt_number(max_players)}" if max_players else ""))
        players_badge.setStyleSheet(
            "background: rgba(139, 92, 246, 0.16); color: #C4B5FD;"
            "border-radius: 10px; padding: 3px 10px; font-weight: 600;"
        )
        top.addWidget(players_badge, 0, Qt.AlignTop)
        layout.addLayout(top)

        # Адрес
        address = QLabel(str(server.get("address") or ""))
        address.setStyleSheet("color: #94A3B8; font-family: Consolas, 'Cascadia Mono', monospace; font-size: 12px;")
        address.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(address)

        # Чипы: версия / регион / источник
        chips = QHBoxLayout()
        chips.setSpacing(6)

        version = str(server.get("version") or "")
        if version:
            chip = QLabel(version)
            chip.setObjectName("SmallBadge")
            chips.addWidget(chip)

        region = str(server.get("region") or "")
        if region:
            chip = QLabel(region)
            chip.setObjectName("SmallBadge")
            chips.addWidget(chip)

        description = str(server.get("description") or "").strip()
        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("InstanceMeta")
            desc_label.setWordWrap(True)
            chips.addWidget(desc_label, 1)

        chips.addStretch()
        layout.addLayout(chips)

        # Кнопки
        actions = QHBoxLayout()
        actions.setSpacing(8)

        copy_button = QPushButton("📋 Копировать адрес")
        copy_button.setObjectName("SecondaryButton")
        copy_button.setCursor(Qt.PointingHandCursor)
        copy_button.clicked.connect(lambda checked=False, s=server, b=copy_button: self._copy_address(s, b))
        actions.addWidget(copy_button)

        link = str(server.get("link") or "")
        if link:
            open_button = QPushButton("↗ Открыть страницу")
            open_button.setObjectName("SecondaryButton")
            open_button.setCursor(Qt.PointingHandCursor)
            open_button.clicked.connect(lambda checked=False, u=link: self._open_link(u))
            actions.addWidget(open_button)

        actions.addStretch()
        layout.addLayout(actions)

        return card

    def _copy_address(self, server, button):
        address = str(server.get("address") or "")
        if not address:
            return
        try:
            QGuiApplication.clipboard().setText(address)
        except Exception:
            return
        button.setText("✓ Скопировано")
        QTimer.singleShot(1600, lambda: button.setText("📋 Копировать адрес"))

    def _open_link(self, url):
        try:
            import webbrowser

            webbrowser.open(url)
        except Exception:
            pass