"""
`PageHeader` — a consistent title + subtitle block used at the top of
every content page (Encrypt, Decrypt, Settings, About).
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PageHeader(QWidget):
    """Renders a page title with an optional descriptive subtitle beneath it."""

    def __init__(self, title: str, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._title_label = QLabel(title, self)
        self._title_label.setProperty("role", "title")
        layout.addWidget(self._title_label)

        self._subtitle_label = QLabel(subtitle, self)
        self._subtitle_label.setProperty("role", "subtitle")
        self._subtitle_label.setVisible(bool(subtitle))
        layout.addWidget(self._subtitle_label)

    def set_title(self, title: str) -> None:
        self._title_label.setText(title)

    def set_subtitle(self, subtitle: str) -> None:
        self._subtitle_label.setText(subtitle)
        self._subtitle_label.setVisible(bool(subtitle))
