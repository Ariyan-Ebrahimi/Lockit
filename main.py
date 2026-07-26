"""
LockIt — Secure File Encryption Desktop Application.

Entry point. Responsible only for bootstrapping: logging, Qt application
setup, high-DPI configuration, and launching the main window. All
business logic lives in `core`, `services`, and `workers`.
"""

from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from config.paths import get_icons_dir
from config.constants import (
    APP_NAME,
    APP_ORGANIZATION,
    APP_ORGANIZATION_DOMAIN,
    APP_VERSION,
)
from ui.styles.theme_manager import ThemeManager
from ui.windows.main_window import MainWindow
from utils.logger import configure_logging, get_logger


def create_application() -> QApplication:
    """Construct and configure the QApplication instance."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORGANIZATION)
    app.setOrganizationDomain(APP_ORGANIZATION_DOMAIN)
    app.setWindowIcon(QIcon(str(get_icons_dir() / "app.ico")))
    ThemeManager.instance().apply(app)
    return app


def main() -> int:
    """Application entry point. Returns the process exit code."""
    configure_logging(verbose="--verbose" in sys.argv)
    logger = get_logger()
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")

    # Load persisted settings before constructing any UI so that
    # EncryptionService / DecryptionService read the correct values
    # from the very first operation.
    from services.settings_service import SettingsService
    SettingsService.instance().load()

    try:
        app = create_application()
        window = MainWindow()
        window.show()
        logger.info("Main window displayed successfully.")
        return app.exec()
    except Exception:
        logger.exception("Fatal error during application startup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
