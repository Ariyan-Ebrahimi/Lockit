"""
LockIt main application window.

Assembles the application shell: a navigation `Sidebar` on the left and
a `QStackedWidget` of content pages on the right. Pages are now fully
functional (Encrypt/Decrypt wired to workers in Phase 5; Settings and
About are static informational pages expanded in Phase 7).
"""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtGui import QCloseEvent, QResizeEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from config.constants import (
    APP_DISPLAY_NAME,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
)
from services.settings_service import SettingsService
from ui.layouts.sidebar import Sidebar
from ui.styles.theme import ThemeColors
from ui.styles.theme_manager import ThemeManager
from ui.widgets.toast_manager import ToastManager
from ui.windows.about_page import AboutPage
from ui.windows.decrypt_page import DecryptPage
from ui.windows.encrypt_page import EncryptPage
from ui.windows.settings_page import SettingsPage
from utils.logger import get_logger

logger = get_logger()

_RESPONSIVE_COLLAPSE_THRESHOLD = 1040


class MainWindow(QMainWindow):
    """Top-level application window for LockIt."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._theme_manager = ThemeManager.instance()
        self._user_collapsed_preference = False
        self._auto_collapsed = False

        self._configure_window()
        self._build_ui()
        self._connect_signals()

        # Toast manager anchored to this window — injected into pages
        self._toast_manager = ToastManager(self)
        self._encrypt_page.set_toast_manager(self._toast_manager)
        self._decrypt_page.set_toast_manager(self._toast_manager)
        self._settings_page.set_toast_manager(self._toast_manager)

        self._sidebar.set_active("encrypt")
        self._content_stack.setCurrentWidget(self._encrypt_page)
        self._apply_theme(self._theme_manager.colors)

        # Restore persisted sidebar state from last session.
        saved_collapsed = SettingsService.instance().settings.sidebar_collapsed
        if saved_collapsed:
            self._user_collapsed_preference = True
            self._sidebar.set_collapsed(True)

    def _configure_window(self) -> None:
        self.setWindowTitle(APP_DISPLAY_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

    def _build_ui(self) -> None:
        central_widget = QWidget(self)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._sidebar = Sidebar(central_widget)
        root_layout.addWidget(self._sidebar)

        self._content_stack = QStackedWidget(central_widget)

        self._encrypt_page = EncryptPage(self._content_stack)
        self._decrypt_page = DecryptPage(self._content_stack)
        self._settings_page = SettingsPage(self._content_stack)

        self._about_page = AboutPage(self._content_stack)

        self._pages: dict[str, QWidget] = {
            "encrypt": self._encrypt_page,
            "decrypt": self._decrypt_page,
            "settings": self._settings_page,
            "about": self._about_page,
        }
        for page in self._pages.values():
            self._content_stack.addWidget(page)

        root_layout.addWidget(self._content_stack, stretch=1)
        self.setCentralWidget(central_widget)

    def _connect_signals(self) -> None:
        self._sidebar.navigation_requested.connect(self._on_navigation_requested)
        self._sidebar.collapse_toggle_requested.connect(self._on_collapse_toggle_requested)
        self._theme_manager.theme_changed.connect(self._apply_theme)

    def _on_navigation_requested(self, key: str) -> None:
        page = self._pages.get(key)
        if page is not None:
            self._content_stack.setCurrentWidget(page)
            self._sidebar.set_active(key)
            logger.debug(f"Navigated to '{key}' page.")

    def _on_collapse_toggle_requested(self) -> None:
        self._user_collapsed_preference = not self._sidebar.is_collapsed
        self._sidebar.set_collapsed(self._user_collapsed_preference)
        self._auto_collapsed = False

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._apply_responsive_layout(event.size())

    def _apply_responsive_layout(self, size: QSize) -> None:
        should_auto_collapse = size.width() < _RESPONSIVE_COLLAPSE_THRESHOLD
        if should_auto_collapse and not self._sidebar.is_collapsed:
            self._sidebar.set_collapsed(True)
            self._auto_collapsed = True
        elif (
            not should_auto_collapse
            and self._auto_collapsed
            and not self._user_collapsed_preference
        ):
            self._sidebar.set_collapsed(False)
            self._auto_collapsed = False

    def closeEvent(self, event: QCloseEvent) -> None:
        logger.info(f"{APP_DISPLAY_NAME} closing.")
        # Persist the sidebar collapsed state for next session.
        SettingsService.instance().update(sidebar_collapsed=self._sidebar.is_collapsed)
        super().closeEvent(event)

    def _apply_theme(self, colors: ThemeColors) -> None:
        self._sidebar.apply_theme(colors)
        self._encrypt_page.apply_theme(colors)
        self._decrypt_page.apply_theme(colors)
        self._settings_page.apply_theme(colors)
        self._about_page.apply_theme(colors)
