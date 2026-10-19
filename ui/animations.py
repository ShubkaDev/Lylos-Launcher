"""Небольшой набор анимаций для интерфейса Lylos Launcher.

Все хелперы безопасны: если виджет уже удалён или анимация прервана,
ошибки не всплывают наружу и не мешают работе приложения.
"""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


def fade_in(
    widget: QWidget,
    duration: int = 220,
    start: float = 0.0,
    end: float = 1.0,
    on_finished=None,
):
    """Плавно проявить виджет (opacity ``start`` → ``end``)."""
    if widget is None:
        return None
    try:
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(start)
        widget.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"opacity", widget)
        animation.setDuration(duration)
        animation.setStartValue(float(start))
        animation.setEndValue(float(end))
        animation.setEasingCurve(QEasingCurve.OutCubic)

        def _cleanup():
            try:
                widget.setGraphicsEffect(None)
            except Exception:
                pass
            if on_finished is not None:
                try:
                    on_finished()
                except Exception:
                    pass

        animation.finished.connect(_cleanup)
        # Держим ссылку, чтобы анимацию не собрал GC.
        widget._fade_animation = animation
        animation.start(QAbstractAnimation.DeleteWhenStopped)
        return animation
    except Exception:
        return None


def animate_size(
    widget: QWidget,
    start_width: int,
    end_width: int,
    duration: int = 220,
    on_finished=None,
):
    """Плавно изменить ширину виджета через min/max (для сайдбара и панелей)."""
    if widget is None:
        return None
    try:
        start_width = int(start_width)
        end_width = int(end_width)
        if start_width == end_width:
            return None

        widget.setMinimumWidth(start_width)
        widget.setMaximumWidth(start_width)

        group = QParallelAnimationGroup(widget)

        for prop in (b"minimumWidth", b"maximumWidth"):
            animation = QPropertyAnimation(widget, prop, group)
            animation.setDuration(duration)
            animation.setStartValue(start_width)
            animation.setEndValue(end_width)
            animation.setEasingCurve(QEasingCurve.InOutCubic)
            group.addAnimation(animation)

        def _cleanup():
            try:
                widget.setMinimumWidth(end_width)
                widget.setMaximumWidth(end_width)
            except Exception:
                pass
            if on_finished is not None:
                try:
                    on_finished()
                except Exception:
                    pass

        group.finished.connect(_cleanup)
        widget._size_animation = group
        group.start(QAbstractAnimation.DeleteWhenStopped)
        return group
    except Exception:
        try:
            widget.setMinimumWidth(end_width)
            widget.setMaximumWidth(end_width)
        except Exception:
            pass
        return None
