"""
`AnimatedButton` — a QPushButton base class with a smoothly animated
hover / checked / active background, used by every custom button in
LockIt (sidebar nav items, icon buttons). Hover feedback is **enabled
by default** so every interactive surface gives clear, immediate visual
confirmation as the pointer moves over it. A subclass may opt out via
`enable_hover=False` for the rare case where hover feedback isn't
wanted.
"""

from __future__ import annotations

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QPushButton, QWidget


class AnimatedButton(QPushButton):
    """
    A checkable/non-checkable button with an animated background colour
    for its hover and checked/active states.

    Paints its own rounded background manually (bypassing QSS for this
    surface only) so `QPropertyAnimation` can interpolate the colour
    smoothly between frames.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        corner_radius: int = 10,
        animation_duration_ms: int = 120,
        enable_hover: bool = True,
    ) -> None:
        super().__init__(parent)
        self._corner_radius = corner_radius
        self._enable_hover = enable_hover
        self._bg_color = QColor(0, 0, 0, 0)
        self._idle_color = QColor(0, 0, 0, 0)
        self._hover_color = QColor(0, 0, 0, 0)
        self._active_color = QColor(0, 0, 0, 0)

        self._animation = QPropertyAnimation(self, b"backgroundColor", self)
        self._animation.setDuration(animation_duration_ms)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    # -- Animated Qt property -------------------------------------------------

    def _get_background_color(self) -> QColor:
        return self._bg_color

    def _set_background_color(self, color: QColor) -> None:
        self._bg_color = color
        self.update()

    backgroundColor = Property(QColor, _get_background_color, _set_background_color)

    # -- Public palette configuration -----------------------------------------

    def set_palette_colors(self, *, idle: QColor, hover: QColor, active: QColor) -> None:
        """Configure the three background states this button animates between."""
        self._idle_color = idle
        self._hover_color = hover
        self._active_color = active
        self._refresh_target_color(animate=False)

    def set_hover_enabled(self, enabled: bool) -> None:
        """Enable or disable the animated hover background at runtime."""
        self._enable_hover = enabled
        if not enabled:
            self._refresh_target_color()

    # -- State transitions ------------------------------------------------------

    def _refresh_target_color(self, *, animate: bool = True) -> None:
        target = self._active_color if self.isChecked() else self._idle_color
        if animate:
            self._animate_to(target)
        else:
            self._bg_color = target
            self.update()

    def _animate_to(self, target: QColor) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._bg_color)
        self._animation.setEndValue(target)
        self._animation.start()

    def enterEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().enterEvent(event)
        if self._enable_hover and not self.isChecked():
            self._animate_to(self._hover_color)

    def leaveEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().leaveEvent(event)
        self._refresh_target_color()

    def setChecked(self, checked: bool) -> None:  # noqa: N802 (Qt override)
        super().setChecked(checked)
        self._refresh_target_color()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        path = QPainterPath()
        path.addRoundedRect(
            self.rect().adjusted(2, 2, -2, -2), self._corner_radius, self._corner_radius
        )
        painter.fillPath(path, self._bg_color)
        painter.end()

        super().paintEvent(event)
