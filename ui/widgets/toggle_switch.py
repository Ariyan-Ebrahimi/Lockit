"""
`ToggleSwitch` — a custom iOS-style on/off toggle painted with
`QPainter`. Emits `toggled(bool)` when the user clicks it.
"""

from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPainterPath
from PySide6.QtWidgets import QSizePolicy, QWidget

_TRACK_W = 42
_TRACK_H = 24
_KNOB_DIAMETER = 18
_KNOB_MARGIN = (_TRACK_H - _KNOB_DIAMETER) // 2

_OFF_TRACK = "#3A3A42"
_ON_TRACK = "#8577F0"
_KNOB = "#FFFFFF"


class ToggleSwitch(QWidget):
    """A painted iOS-style toggle switch."""

    toggled = Signal(bool)

    def __init__(self, checked: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._checked = checked
        self._knob_x: float = self._target_knob_x(checked)

        self.setFixedSize(QSize(_TRACK_W, _TRACK_H))
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim = QPropertyAnimation(self, b"knobX", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ------------------------------------------------------------------
    # Qt property so QPropertyAnimation can drive the knob
    # ------------------------------------------------------------------

    def _get_knob_x(self) -> float:
        return self._knob_x

    def _set_knob_x(self, value: float) -> None:
        self._knob_x = value
        self.update()

    knobX = Property(float, _get_knob_x, _set_knob_x)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_checked(self) -> bool:
        return self._checked

    def set_checked(self, checked: bool, *, emit: bool = False) -> None:
        if checked == self._checked:
            return
        self._checked = checked
        self._animate_to(checked)
        if emit:
            self.toggled.emit(checked)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _target_knob_x(checked: bool) -> float:
        if checked:
            return _TRACK_W - _KNOB_DIAMETER - _KNOB_MARGIN
        return float(_KNOB_MARGIN)

    def _animate_to(self, checked: bool) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._knob_x)
        self._anim.setEndValue(self._target_knob_x(checked))
        self._anim.start()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_checked(not self._checked, emit=True)
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Track
        track_color = QColor(_ON_TRACK if self._checked else _OFF_TRACK)
        track_path = QPainterPath()
        track_path.addRoundedRect(QRect(0, 0, _TRACK_W, _TRACK_H), _TRACK_H / 2, _TRACK_H / 2)
        painter.fillPath(track_path, track_color)

        # Knob
        knob_x = int(self._knob_x)
        knob_rect = QRect(knob_x, _KNOB_MARGIN, _KNOB_DIAMETER, _KNOB_DIAMETER)
        knob_path = QPainterPath()
        knob_path.addEllipse(knob_rect)
        painter.fillPath(knob_path, QColor(_KNOB))

        painter.end()
