"""
`NavButton` — a checkable sidebar navigation item combining an icon and
a label, with an animated hover/active background and theme-aware icon
recoloring.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from ui.styles.theme import ThemeColors
from ui.widgets.animated_button import AnimatedButton
from utils.icon_loader import load_svg_icon


class NavButton(AnimatedButton):
    """A single entry in the sidebar (e.g. 'Encrypt', 'Decrypt', 'Settings')."""

    def __init__(
        self,
        *,
        key: str,
        label: str,
        icon_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            parent, corner_radius=10, enable_hover=False, animation_duration_ms=0
        )
        self.key = key
        self._label = label
        self._icon_path = icon_path
        self._last_colors: ThemeColors | None = None

        self.setCheckable(True)
        self.setText(f"  {label}")
        self.setIconSize(QSize(19, 19))
        self.setMinimumHeight(42)
        self.setStyleSheet(self._button_qss())
        self.setToolTip(label)

    def set_collapsed(self, collapsed: bool) -> None:
        """Show icon-only (collapsed) or icon+label (expanded)."""
        self.setText("" if collapsed else f"  {self._label}")

    def _button_qss(self) -> str:
        # Text/icon layer only — background is hand-painted by AnimatedButton.
        return """
            QPushButton {
                text-align: left;
                padding-left: 12px;
                border: none;
                background: transparent;
                font-size: 13px;
                font-weight: 500;
            }
        """

    def apply_theme(self, colors: ThemeColors) -> None:
        """Refresh icon tint and background palette for the active theme."""
        self._last_colors = colors
        is_active = self.isChecked()
        text_color = colors.sidebar_text_active if is_active else colors.sidebar_text
        self.setStyleSheet(
            self._button_qss()
            + f"QPushButton {{ color: {text_color}; }}"
        )

        icon_color = QColor(colors.sidebar_text_active if is_active else colors.sidebar_text)
        self.setIcon(load_svg_icon(self._icon_path, icon_color, size=19))

        self.set_palette_colors(
            idle=QColor(0, 0, 0, 0),
            hover=QColor(0, 0, 0, 0),  # sidebar has no hover state by design
            active=QColor(colors.sidebar_active_bg),
        )

    def setChecked(self, checked: bool) -> None:  # noqa: N802 (Qt override)
        super().setChecked(checked)
        # Re-apply text/icon color for the new checked state if we already
        # have a theme (apply_theme sets _last_colors via closure below).
        if self._last_colors is not None:
            self.apply_theme(self._last_colors)
