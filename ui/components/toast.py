
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel


class Toast(QLabel):
    """Всплывающее уведомление с плавным появлением и исчезновением."""

    def __init__(self, parent, title, text):
        super().__init__(parent)
        self.setText(f"{title}\n{text}")
        self.setObjectName("Panel")
        self.setStyleSheet("padding:14px; border-radius:14px;")
        self.adjustSize()
        self._opacity_effect = None
        self._animation = None

    def show_toast(self):
        parent = self.parent()
        self.adjustSize()
        self.move(parent.width() - self.width() - 30, 100)
        self.show()
        self._fade(0.0, 1.0, 180)
        QTimer.singleShot(2400, self._hide_toast)

    def _fade(self, start: float, end: float, duration: int, on_finished=None):
        try:
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(start)
            self.setGraphicsEffect(effect)
            animation = QPropertyAnimation(effect, b"opacity", self)
            animation.setDuration(duration)
            animation.setStartValue(start)
            animation.setEndValue(end)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            if on_finished is not None:
                animation.finished.connect(on_finished)
            self._opacity_effect = effect
            self._animation = animation
            animation.start()
        except Exception:
            if on_finished is not None:
                on_finished()

    def _hide_toast(self):
        self._fade(1.0, 0.0, 220, self.deleteLater)
