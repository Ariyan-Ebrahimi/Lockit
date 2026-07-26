"""
`PasswordStrengthWidget` — a polished password-strength indicator
combining five animated segment bars, a tier label, and an inline
feedback message. Designed to replace the minimal `_StrengthBar` in
`EncryptPage` with a fully self-contained, reusable component.
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Property
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from core.security.password_strength import PasswordStrength, PasswordStrengthResult

_TIER_LABEL: dict[PasswordStrength, str] = {
    PasswordStrength.VERY_WEAK: "Very Weak",
    PasswordStrength.WEAK: "Weak",
    PasswordStrength.FAIR: "Fair",
    PasswordStrength.STRONG: "Strong",
    PasswordStrength.VERY_STRONG: "Very Strong",
}

_TIER_COLOR: dict[PasswordStrength, str] = {
    PasswordStrength.VERY_WEAK: "#F0666B",
    PasswordStrength.WEAK: "#E8B54C",
    PasswordStrength.FAIR: "#E8B54C",
    PasswordStrength.STRONG: "#3DC98A",
    PasswordStrength.VERY_STRONG: "#3DC98A",
}


class _Segment(QWidget):
    """A single rounded bar segment with an animated fill level (0.0–1.0)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(5)
        self._fill: float = 0.0
        self._color = QColor("#2E2E35")
        self._track_color = QColor("#2E2E35")

        self._anim = QPropertyAnimation(self, b"fill", self)
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _get_fill(self) -> float:
        return self._fill

    def _set_fill(self, value: float) -> None:
        self._fill = max(0.0, min(1.0, value))
        self.update()

    fill = Property(float, _get_fill, _set_fill)

    def animate_to(self, target: float, color: QColor) -> None:
        self._color = color
        self._anim.stop()
        self._anim.setStartValue(self._fill)
        self._anim.setEndValue(target)
        self._anim.start()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        radius = r.height() / 2

        # Track
        track = QPainterPath()
        track.addRoundedRect(r, radius, radius)
        painter.fillPath(track, self._track_color)

        # Fill
        if self._fill > 0:
            fill_rect = QRect(r.left(), r.top(), int(r.width() * self._fill), r.height())
            fill_path = QPainterPath()
            fill_path.addRoundedRect(fill_rect, radius, radius)
            painter.fillPath(fill_path, self._color)

        painter.end()


class PasswordStrengthWidget(QWidget):
    """
    Self-contained password strength display: five segment bars +
    tier name label + feedback message.
    """

    _SEGMENT_COUNT = 5

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._segments: list[_Segment] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(6)

        # Header row: "Password Strength" label + tier label (right-aligned)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        strength_lbl = QLabel("Password strength", self)
        strength_lbl.setStyleSheet("font-size: 11px; color: #7C7C88;")
        header.addWidget(strength_lbl)
        header.addStretch(1)
        self._tier_label = QLabel("", self)
        self._tier_label.setStyleSheet("font-size: 11px; font-weight: 600;")
        header.addWidget(self._tier_label)
        layout.addLayout(header)

        # Segments row
        seg_row = QHBoxLayout()
        seg_row.setContentsMargins(0, 0, 0, 0)
        seg_row.setSpacing(5)
        for _ in range(self._SEGMENT_COUNT):
            seg = _Segment(self)
            self._segments.append(seg)
            seg_row.addWidget(seg)
        layout.addLayout(seg_row)

        # Feedback message
        self._feedback_label = QLabel("", self)
        self._feedback_label.setWordWrap(True)
        self._feedback_label.setStyleSheet("font-size: 11px; color: #7C7C88;")
        layout.addWidget(self._feedback_label)

    def update_result(self, result: PasswordStrengthResult | None) -> None:
        """
        Refresh the widget for a new strength result.

        Pass `None` to reset to the empty/blank state (e.g. when the
        password field is cleared).
        """
        if result is None:
            for seg in self._segments:
                seg.animate_to(0.0, QColor("#2E2E35"))
            self._tier_label.setText("")
            self._tier_label.setStyleSheet("font-size: 11px; font-weight: 600;")
            self._feedback_label.setText("")
            return

        tier = result.strength
        color = QColor(_TIER_COLOR[tier])
        filled_count = int(tier) + 1  # VERY_WEAK=1 bar, VERY_STRONG=5 bars

        for i, seg in enumerate(self._segments):
            seg.animate_to(1.0 if i < filled_count else 0.0, color)

        self._tier_label.setText(_TIER_LABEL[tier])
        self._tier_label.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {_TIER_COLOR[tier]};"
        )

        feedback = " ".join(result.feedback)
        # Show positive feedback in success colour; warnings in muted
        if tier >= PasswordStrength.STRONG and not result.feedback:
            self._feedback_label.setText("")
        else:
            self._feedback_label.setText(feedback)
