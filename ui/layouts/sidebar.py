"""
`Sidebar` — the primary navigation surface for LockIt: app branding,
section navigation, and a footer with theme/collapse controls. Animates
smoothly between its expanded and collapsed widths.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Signal,
)
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from config.constants import SIDEBAR_WIDTH_COLLAPSED, SIDEBAR_WIDTH_EXPANDED
from config.paths import get_icons_dir
from ui.styles.theme import ThemeColors
from ui.widgets.icon_button import IconButton
from ui.widgets.nav_button import NavButton
from utils.icon_loader import load_svg_icon


@dataclass(frozen=True, slots=True)
class NavItem:
    """Declarative description of one sidebar navigation entry."""

    key: str
    label: str
    icon_file: str


NAV_ITEMS: tuple[NavItem, ...] = (
    NavItem(key="encrypt", label="Encrypt", icon_file="lock.svg"),
    NavItem(key="decrypt", label="Decrypt", icon_file="unlock.svg"),
    NavItem(key="settings", label="Settings", icon_file="settings.svg"),
    NavItem(key="about", label="About", icon_file="info.svg"),
)


class Sidebar(QFrame):
    """
    Application sidebar with logo, navigation buttons, and a footer
    holding the theme-cycle and collapse-toggle controls.
    """

    navigation_requested = Signal(str)
    collapse_toggle_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self._collapsed = False
        self._icons_dir = get_icons_dir()
        self._nav_buttons: dict[str, NavButton] = {}
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._last_colors: ThemeColors | None = None

        self._width_animation = QPropertyAnimation(self, b"minimumWidth", self)
        self._width_animation.setDuration(180)
        self._width_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._max_width_animation = QPropertyAnimation(self, b"maximumWidth", self)
        self._max_width_animation.setDuration(180)
        self._max_width_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._build_ui()
        self.setMinimumWidth(SIDEBAR_WIDTH_EXPANDED)
        self.setMaximumWidth(SIDEBAR_WIDTH_EXPANDED)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 18, 14, 14)
        root.setSpacing(6)

        root.addWidget(self._build_logo_row())
        root.addSpacing(18)

        for item in NAV_ITEMS:
            button = NavButton(
                key=item.key,
                label=item.label,
                icon_path=self._icons_dir / item.icon_file,
            )
            button.clicked.connect(lambda _checked, k=item.key: self.navigation_requested.emit(k))
            self._button_group.addButton(button)
            self._nav_buttons[item.key] = button
            root.addWidget(button)

        root.addStretch(1)
        root.addWidget(self._build_footer())

    def _build_logo_row(self) -> QWidget:
        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(6, 0, 0, 0)
        layout.setSpacing(10)

        self._logo_icon_label = QLabel(row)
        self._logo_icon_label.setFixedSize(24, 24)
        layout.addWidget(self._logo_icon_label)

        self._logo_text_label = QLabel("LockIt", row)
        self._logo_text_label.setObjectName("SidebarLogoLabel")
        layout.addWidget(self._logo_text_label)
        layout.addStretch(1)

        self._logo_row = row
        return row

    def _build_footer(self) -> QWidget:
        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(4, 8, 4, 4)
        layout.setSpacing(8)

        layout.addStretch(1)

        self._collapse_button = IconButton(
            icon_path=self._icons_dir / "chevron-left.svg",
            tooltip="Collapse sidebar",
            diameter=30,
            icon_size=15,
        )
        self._collapse_button.clicked.connect(self.collapse_toggle_requested.emit)
        layout.addWidget(self._collapse_button)

        self._footer_row = row
        return row

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_active(self, key: str) -> None:
        """
        Mark the given navigation key as the active/checked section.

        Explicitly sets every button's checked state (rather than
        checking only the target and trusting QButtonGroup's implicit
        exclusivity to unset the rest) so the sidebar highlight can
        never drift out of sync with the visible page.
        """
        for button_key, button in self._nav_buttons.items():
            button.setChecked(button_key == key)

    def set_collapsed(self, collapsed: bool) -> None:
        """Animate the sidebar between its expanded and collapsed widths."""
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed

        target_width = SIDEBAR_WIDTH_COLLAPSED if collapsed else SIDEBAR_WIDTH_EXPANDED
        for animation in (self._width_animation, self._max_width_animation):
            animation.stop()
            animation.setStartValue(self.width())
            animation.setEndValue(target_width)
            animation.start()

        self._logo_text_label.setVisible(not collapsed)
        for button in self._nav_buttons.values():
            button.set_collapsed(collapsed)

        icon_path = self._icons_dir / ("chevron-right.svg" if collapsed else "chevron-left.svg")
        self._collapse_button.set_icon_path(icon_path)
        if self._last_colors is not None:
            self._collapse_button.apply_theme(self._last_colors)

    @property
    def is_collapsed(self) -> bool:
        return self._collapsed

    def apply_theme(self, colors: ThemeColors) -> None:
        """Propagate the active theme palette to every child widget."""
        self._last_colors = colors

        icon = load_svg_icon(self._icons_dir / "shield.svg", QColor(colors.accent), size=22)
        self._logo_icon_label.setPixmap(icon.pixmap(22, 22))

        for button in self._nav_buttons.values():
            button.apply_theme(colors)

        self._collapse_button.apply_theme(colors)
