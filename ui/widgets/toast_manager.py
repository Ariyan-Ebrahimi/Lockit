"""
`ToastManager` — manages a stack of `Toast` notifications anchored to a
parent window, repositioning them as each one is dismissed so they
never overlap.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QPoint
from PySide6.QtWidgets import QWidget

from ui.widgets.toast import Toast, ToastKind

_MARGIN_RIGHT = 20
_MARGIN_BOTTOM = 20
_GAP = 10


class ToastManager(QObject):
    """Owns and positions the active toast stack for one window."""

    def __init__(self, anchor: QWidget) -> None:
        super().__init__(anchor)
        self._anchor = anchor
        self._stack: list[Toast] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def success(self, title: str, message: str = "") -> None:
        self._show(ToastKind.SUCCESS, title, message)

    def error(self, title: str, message: str = "") -> None:
        self._show(ToastKind.ERROR, title, message)

    def warning(self, title: str, message: str = "") -> None:
        self._show(ToastKind.WARNING, title, message)

    def info(self, title: str, message: str = "") -> None:
        self._show(ToastKind.INFO, title, message)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _show(self, kind: ToastKind, title: str, message: str) -> None:
        toast = Toast(kind=kind, title=title, message=message, parent=self._anchor)
        toast.dismissed.connect(lambda t=toast: self._on_dismissed(t))
        self._stack.append(toast)
        self._reposition_all()
        toast.show_at(self._position_for(len(self._stack) - 1, toast))

    def _on_dismissed(self, toast: Toast) -> None:
        if toast in self._stack:
            self._stack.remove(toast)
        toast.deleteLater()
        self._reposition_all()

    def _reposition_all(self) -> None:
        for i, toast in enumerate(self._stack):
            target = self._position_for(i, toast)
            if toast.isVisible():
                toast.move(target)

    def _position_for(self, index: int, toast: Toast) -> QPoint:
        """Position toast `index` from the bottom-right of the anchor."""
        anchor_rect = self._anchor.rect()
        anchor_pos = self._anchor.mapToGlobal(anchor_rect.bottomRight())

        # Stack upward: each toast sits above the previous one
        y_offset = _MARGIN_BOTTOM + index * (toast.sizeHint().height() + _GAP)
        x = anchor_pos.x() - toast.width() - _MARGIN_RIGHT
        y = anchor_pos.y() - y_offset - toast.sizeHint().height()
        return QPoint(x, y)
