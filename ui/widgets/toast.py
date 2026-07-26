"""
`Toast` — a self-dismissing notification widget that slides in from the
bottom-right of the screen, displays a message with a semantic icon and
a coloured left-accent bar, then fades out automatically.

Used for non-blocking feedback after encrypt/decrypt operations succeed
or fail — replacing the disruptive `QMessageBox.critical` / `.information`
pattern for routine outcomes (Phase 5 pages still use QMessageBox for
the *confirmational* overwrite prompt, which is intentionally blocking).
"""

from __future__ import annotations

from enum import Enum, auto

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    QTimer,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from config.paths import get_icons_dir
from utils.icon_loader import load_svg_icon


class ToastKind(Enum):
    SUCCESS = auto()
    ERROR = auto()
    WARNING = auto()
    INFO = auto()


_KIND_ICON: dict[ToastKind, str] = {
    ToastKind.SUCCESS: "shield.svg",
    ToastKind.ERROR: "info.svg",
    ToastKind.WARNING: "info.svg",
    ToastKind.INFO: "info.svg",
}

_KIND_COLOR: dict[ToastKind, str] = {
    ToastKind.SUCCESS: "#3DC98A",
    ToastKind.ERROR: "#F0666B",
    ToastKind.WARNING: "#E8B54C",
    ToastKind.INFO: "#8577F0",
}

_AUTO_DISMISS_MS = 4500
_FADE_DURATION_MS = 280
_SLIDE_DURATION_MS = 300
_WIDTH = 360
_HEIGHT = 72


class Toast(QWidget):
    """A single animated toast notification."""

    dismissed = Signal()

    def __init__(
        self,
        *,
        kind: ToastKind,
        title: str,
        message: str = "",
        parent: QWidget,
    ) -> None:
        super().__init__(parent, Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(_WIDTH)

        self._kind = kind
        self._accent_color = QColor(_KIND_COLOR[kind])

        self._build_ui(title, message)
        self.adjustSize()

        # Opacity animation for fade-in / fade-out
        self._opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._opacity_anim.setDuration(_FADE_DURATION_MS)
        self._opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Slide animation (move upward on show)
        self._pos_anim = QPropertyAnimation(self, b"pos", self)
        self._pos_anim.setDuration(_SLIDE_DURATION_MS)
        self._pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Auto-dismiss timer
        self._dismiss_timer = QTimer(self)
        self._dismiss_timer.setSingleShot(True)
        self._dismiss_timer.setInterval(_AUTO_DISMISS_MS)
        self._dismiss_timer.timeout.connect(self._start_dismiss)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_ui(self, title: str, message: str) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(12)

        icons_dir = get_icons_dir()
        icon_file = _KIND_ICON[self._kind]
        icon_label = QLabel(self)
        icon_label.setFixedSize(22, 22)
        px = load_svg_icon(icons_dir / icon_file, self._accent_color, size=18)
        icon_label.setPixmap(px.pixmap(18, 18))
        outer.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_label = QLabel(title, self)
        title_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        text_col.addWidget(title_label)

        if message:
            msg_label = QLabel(message, self)
            msg_label.setWordWrap(True)
            msg_label.setStyleSheet("font-size: 12px; color: #B4B4BE;")
            text_col.addWidget(msg_label)

        outer.addLayout(text_col, stretch=1)

        close_label = QLabel("✕", self)
        close_label.setStyleSheet("font-size: 12px; color: #7C7C88; padding: 2px;")
        close_label.setCursor(Qt.CursorShape.PointingHandCursor)
        close_label.mousePressEvent = lambda _: self._start_dismiss()
        outer.addWidget(close_label, alignment=Qt.AlignmentFlag.AlignTop)

    # ------------------------------------------------------------------
    # Paint — card background + left accent stripe
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)

        # Card background
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        painter.fillPath(path, QColor("#1E1E23"))

        # Border
        from PySide6.QtGui import QPen
        painter.setPen(QPen(QColor("#2E2E35"), 1))
        painter.drawPath(path)

        # Left accent stripe
        stripe = QPainterPath()
        stripe.addRoundedRect(QRect(rect.left(), rect.top() + 10, 4, rect.height() - 20), 2, 2)
        painter.fillPath(stripe, self._accent_color)
        painter.end()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def show_at(self, pos: QPoint) -> None:
        """Slide the toast in from slightly below `pos`."""
        slide_start = QPoint(pos.x(), pos.y() + 20)
        self.move(slide_start)
        self.setWindowOpacity(0.0)
        self.show()

        self._pos_anim.setStartValue(slide_start)
        self._pos_anim.setEndValue(pos)
        self._pos_anim.start()

        self._opacity_anim.setStartValue(0.0)
        self._opacity_anim.setEndValue(1.0)
        self._opacity_anim.start()

        self._dismiss_timer.start()

    def _start_dismiss(self) -> None:
        self._dismiss_timer.stop()
        self._opacity_anim.setStartValue(self.windowOpacity())
        self._opacity_anim.setEndValue(0.0)
        self._opacity_anim.finished.connect(self._on_fade_out_done)
        self._opacity_anim.start()

    def _on_fade_out_done(self) -> None:
        self.hide()
        self.dismissed.emit()
