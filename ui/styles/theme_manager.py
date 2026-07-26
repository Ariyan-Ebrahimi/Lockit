"""
Theme management for LockIt.

`ThemeManager` is the single source of truth for the application's
active (always dark) palette. It applies the generated QSS to the
`QApplication` and notifies subscribers via a Qt signal so that custom
widgets (which draw icons manually) can refresh themselves.

Usage:
    theme_manager = ThemeManager.instance()
    theme_manager.apply(app)
    theme_manager.theme_changed.connect(my_widget.on_theme_changed)
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from ui.styles.stylesheet_builder import build_stylesheet
from ui.styles.theme import ThemeColors, ThemeMode, get_palette
from utils.logger import get_logger

logger = get_logger()


class ThemeManager(QObject):
    """
    Singleton responsible for applying and broadcasting the
    application's (single, dark) theme.
    """

    theme_changed = Signal(ThemeColors)

    _instance: "ThemeManager | None" = None

    def __init__(self) -> None:
        super().__init__()
        self._mode: ThemeMode = ThemeMode.DARK
        self._colors: ThemeColors = get_palette(self._mode)

    @classmethod
    def instance(cls) -> "ThemeManager":
        """Return the shared ThemeManager instance, creating it if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def mode(self) -> ThemeMode:
        """The application's theme mode (always DARK)."""
        return self._mode

    @property
    def colors(self) -> ThemeColors:
        """The currently active, resolved color palette."""
        return self._colors

    @property
    def is_dark(self) -> bool:
        """Whether the currently resolved theme is dark (always True)."""
        return True

    def apply(self, app: QApplication, mode: ThemeMode | None = None) -> None:
        """Apply the (dark) theme to the QApplication."""
        self._colors = get_palette(self._mode)
        app.setStyleSheet(build_stylesheet(self._colors))
        logger.info("Applied dark theme to application.")

    def tint_color(self, *, secondary: bool = False, muted: bool = False) -> QColor:
        """Convenience accessor for the current text color, for manual icon painting."""
        if muted:
            return QColor(self._colors.text_muted)
        if secondary:
            return QColor(self._colors.text_secondary)
        return QColor(self._colors.text_primary)
