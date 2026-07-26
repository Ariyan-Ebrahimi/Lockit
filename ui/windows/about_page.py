"""
`AboutPage` — About LockIt.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config.constants import APP_NAME, APP_VERSION
from config.paths import get_icons_dir
from ui.styles.theme import ThemeColors
from utils.icon_loader import load_svg_icon


class AboutPage(QScrollArea):
    """About page — app identity, purpose, and feature highlights."""

    def __init__(self, parent: QWidget | None = None) -> None:
        self._icon_badge: QLabel
        self._feature_icon_labels: list[QLabel] = []
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self._icons_dir = get_icons_dir()
        self._build_ui()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(48, 48, 48, 48)
        root.setSpacing(0)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        root.addWidget(self._build_hero())
        root.addSpacing(48)
        root.addWidget(self._build_features())
        root.addSpacing(48)
        root.addWidget(self._build_footer())

        self.setWidget(container)

    def _build_hero(self) -> QWidget:
        hero = QWidget()
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Shield icon badge
        self._icon_badge = QLabel()
        self._icon_badge.setFixedSize(88, 88)
        self._icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_badge.setStyleSheet(
            "background-color: #2B2755;"
            "border-radius: 22px;"
        )
        layout.addWidget(self._icon_badge, alignment=Qt.AlignmentFlag.AlignHCenter)

        # App name
        name = QLabel(APP_NAME)
        name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        name.setStyleSheet(
            "font-size: 36px;"
            "font-weight: 700;"
            "color: #F2F2F5;"
            "letter-spacing: -0.5px;"
        )
        layout.addWidget(name)

        # Tagline
        tagline = QLabel("Keep your files private.\nAlways.")
        tagline.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        tagline.setStyleSheet(
            "font-size: 16px;"
            "color: #7C7C88;"
            "line-height: 160%;"
        )
        layout.addWidget(tagline)

        # Version pill
        version = QLabel(f"Version {APP_VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        version.setFixedHeight(28)
        version.setStyleSheet(
            "font-size: 11px;"
            "font-weight: 600;"
            "color: #8577F0;"
            "background-color: #2B2755;"
            "border-radius: 14px;"
            "padding: 0 14px;"
        )
        layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignHCenter)

        return hero

    def _build_features(self) -> QWidget:
        """Three side-by-side feature cards."""
        items = [
            ("lock.svg",   "Strong Encryption",     "Every file is encrypted with AES-256, one of the strongest standards available today."),
            ("shield.svg", "Private by Design",     "Your password never leaves your device. Nothing is sent to any server. Ever."),
            ("unlock.svg", "Works with Any File",   "Encrypt documents, photos, videos, archives — any file type, no restrictions."),
        ]

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        for icon_file, title, body in items:
            card, icon_label = self._feature_card(icon_file, title, body)
            self._feature_icon_labels.append((icon_label, icon_file))
            layout.addWidget(card)

        return row

    def _feature_card(self, icon_file: str, title: str, body: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setProperty("role", "card")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(
            "background-color: #2B2755;"
            "border-radius: 10px;"
        )
        layout.addWidget(icon_label)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 14px;"
            "font-weight: 700;"
            "color: #F2F2F5;"
        )
        layout.addWidget(title_lbl)

        # Body
        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(
            "font-size: 12px;"
            "color: #7C7C88;"
            "line-height: 160%;"
        )
        layout.addWidget(body_lbl)

        return card, icon_label

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        layout = QVBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        line = QFrame()
        line.setProperty("role", "separator")
        layout.addWidget(line)
        layout.addSpacing(24)

        copy = QLabel(f"© 2026 {APP_NAME}. All rights reserved.")
        copy.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        copy.setStyleSheet("font-size: 12px; color: #4A4A54;")
        layout.addWidget(copy)

        return footer

    # ------------------------------------------------------------------
    # Theming
    # ------------------------------------------------------------------

    def apply_theme(self, colors: ThemeColors) -> None:
        shield = load_svg_icon(
            self._icons_dir / "shield.svg", QColor(colors.accent), size=44
        )
        self._icon_badge.setPixmap(shield.pixmap(44, 44))

        for icon_label, icon_file in self._feature_icon_labels:
            icon = load_svg_icon(
                self._icons_dir / icon_file, QColor(colors.accent), size=20
            )
            icon_label.setPixmap(icon.pixmap(20, 20))
