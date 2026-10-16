from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget


class LoadingAnimation(QWidget):
    """Анимированный индикатор загрузки: двухцветный спиннер + бегущие точки.

    Используется на страницах каталогов (моды, сервера), чтобы вместо
    пустого текста «каталог не загрузился…» показывать живую анимацию.
    """

    def __init__(self, parent=None, text_prefix="Загрузка", subtitle="Поиск..."):
        super().__init__(parent)
        self._prefix = text_prefix
        self._subtitle = subtitle
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._angle = 0
        self._label_index = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)

    def _labels(self):
        return [
            self._prefix,
            f"{self._prefix} •",
            f"{self._prefix} ••",
            f"{self._prefix} •••",
        ]

    def _tick(self):
        self._angle = (self._angle + 10) % 360
        labels = self._labels()
        self._label_index = (self._label_index + 1) % len(labels)
        self.update()

    def stop_animation(self):
        self._timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx = self.rect().center().x()
        cy = self.rect().center().y() - 24

        radius = 30
        pen_width = 7

        track = QPen(QColor("#1C2740"), pen_width, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(track)
        painter.drawArc(cx - radius, cy - radius, radius * 2, radius * 2, 0, 360 * 16)

        violet = QPen(QColor("#8B5CF6"), pen_width, Qt.SolidLine, Qt.RoundCap)
        cyan = QPen(QColor("#22D3EE"), pen_width, Qt.SolidLine, Qt.RoundCap)

        start = -self._angle * 16
        painter.setPen(violet)
        painter.drawArc(cx - radius, cy - radius, radius * 2, radius * 2, start, 150 * 16)
        painter.setPen(cyan)
        painter.drawArc(cx - radius, cy - radius, radius * 2, radius * 2, start + 150 * 16, 130 * 16)

        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        metrics = QFontMetrics(font)

        labels = self._labels()
        text = labels[self._label_index % len(labels)]
        text_x = cx - metrics.horizontalAdvance(text) // 2
        text_y = cy + radius + 42

        painter.setPen(QColor("#F5F3FF"))
        painter.drawText(text_x, text_y, text)

        sub = self._subtitle
        painter.setPen(QColor("#94A3B8"))
        painter.drawText(cx - metrics.horizontalAdvance(sub) // 2, text_y + 26, sub)