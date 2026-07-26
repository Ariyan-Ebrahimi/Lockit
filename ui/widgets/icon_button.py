"""
`IconButton` — a small, round, icon-only button used for secondary
actions such as the sidebar collapse control. No hover state, by
design — only the pressed state animates, keeping the sidebar calm.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from ui.styles.theme import ThemeColors
from ui.widgets.animated_button import AnimatedButton
from utils.icon_loader import load_svg_icon


class IconButton(AnimatedButton):
    """A compact, circular icon button (e.g. sidebar collapse arrow)."""

    def __init__(
        self,
        *,
        icon_path: Path,
        tooltip: str = "",
        diameter: int = 34,
        icon_size: int = 17,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent, corner_radius=diameter // 2, enable_hover=False)
        self._icon_path = icon_path
        self._icon_size = icon_size

        self.setFixedSize(QSize(diameter, diameter))
        self.setStyleSheet("QPushButton { border: none; background: transparent; }")
        if tooltip:
            self.setToolTip(tooltip)

    def set_icon_path(self, icon_path: Path) -> None:
        """Swap the icon graphic."""
        self._icon_path = icon_path

    def apply_theme(self, colors: ThemeColors, *, icon_color: str | None = None) -> None:
        """Refresh icon tint. No hover — only the pressed state animates."""
        color = QColor(icon_color if icon_color else colors.text_secondary)
        self.setIcon(load_svg_icon(self._icon_path, color, size=self._icon_size))
        self.setIconSize(QSize(self._icon_size, self._icon_size))

        transparent = QColor(0, 0, 0, 0)
        self.set_palette_colors(
            idle=transparent,
            hover=transparent,
            active=QColor(colors.surface_pressed),
        )
