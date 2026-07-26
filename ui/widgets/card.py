"""
`Card` — a reusable rounded, bordered surface container used to group
related content throughout the application (matches the QSS role
"card" defined in stylesheet_builder.py).
"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget


class Card(QFrame):
    """A rounded, bordered content container with sensible default padding."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        padding: int = 20,
        spacing: int = 12,
    ) -> None:
        super().__init__(parent)
        self.setProperty("role", "card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(padding, padding, padding, padding)
        self._layout.setSpacing(spacing)

    @property
    def body_layout(self) -> QVBoxLayout:
        """The layout new content should be added to."""
        return self._layout
