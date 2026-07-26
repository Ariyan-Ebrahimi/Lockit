"""
`InfoPage` — the scaffolded content shown for each sidebar section in
Phase 2. Encrypt/Decrypt pages will be replaced with full functionality
in Phase 5; Settings gains real controls in Phase 7. About is a
genuine, permanent page.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from ui.widgets.card import Card
from ui.widgets.page_header import PageHeader
from utils.icon_loader import load_svg_icon


class InfoPage(QScrollArea):
    """A scrollable page with a header, an icon badge, and body content."""

    def __init__(
        self,
        *,
        title: str,
        subtitle: str,
        icon_path: Path,
        body_text: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._icon_path = icon_path
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        outer_layout = QVBoxLayout(container)
        outer_layout.setContentsMargins(32, 28, 32, 28)
        outer_layout.setSpacing(20)

        outer_layout.addWidget(PageHeader(title, subtitle))

        self._badge_label = QLabel()
        self._badge_label.setFixedSize(56, 56)
        outer_layout.addWidget(self._badge_label, alignment=Qt.AlignmentFlag.AlignLeft)

        card = Card()
        body_label = QLabel(body_text)
        body_label.setWordWrap(True)
        body_label.setProperty("role", "subtitle")
        card.body_layout.addWidget(body_label)
        outer_layout.addWidget(card)

        outer_layout.addStretch(1)
        self.setWidget(container)

    def apply_theme(self, accent_color: str, surface_soft: str) -> None:
        """Recolor the icon badge for the active theme."""
        icon = load_svg_icon(self._icon_path, QColor(accent_color), size=26)
        self._badge_label.setPixmap(icon.pixmap(26, 26))
        self._badge_label.setStyleSheet(
            f"background-color: {surface_soft}; border-radius: 14px; padding: 15px;"
        )
