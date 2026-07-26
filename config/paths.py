"""
Cross-platform path resolution for LockIt.

Centralizes every filesystem location the application depends on so that
no other module has to hardcode or re-derive a path. This keeps the app
portable across Windows, Linux, and macOS.
"""

from __future__ import annotations

import sys
from pathlib import Path

from config.constants import APP_NAME, LOG_FILE_NAME


def _is_frozen() -> bool:
    """Return True when running from a PyInstaller-frozen executable."""
    return bool(getattr(sys, "frozen", False))


def get_project_root() -> Path:
    """
    Return the root directory of the LockIt source tree.

    When frozen by PyInstaller, this resolves relative to the executable;
    otherwise it resolves relative to this file's location.
    """
    if _is_frozen():
        # PyInstaller extracts/bundles runtime data under sys._MEIPASS.
        # In modern onedir builds this is commonly dist/LockIt/_internal,
        # so resolving assets relative to the executable directory would
        # make SVG/icon files appear missing after installation.
        bundle_dir = getattr(sys, "_MEIPASS", None)
        if bundle_dir:
            return Path(bundle_dir).resolve()
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_assets_dir() -> Path:
    """Return the directory containing static assets (icons, images, fonts)."""
    return get_project_root() / "assets"


def get_icons_dir() -> Path:
    """Return the directory containing UI icons."""
    return get_assets_dir() / "icons"


def get_images_dir() -> Path:
    """Return the directory containing UI images."""
    return get_assets_dir() / "images"


def get_fonts_dir() -> Path:
    """Return the directory containing bundled fonts."""
    return get_assets_dir() / "fonts"


def get_user_data_dir() -> Path:
    """
    Return the per-user, per-OS directory for LockIt's persistent data
    (settings, logs). Created on first access if it does not exist.

    - Windows: %APPDATA%\\LockIt
    - macOS:   ~/Library/Application Support/LockIt
    - Linux:   ~/.local/share/LockIt (XDG Base Directory spec)
    """
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    data_dir = base / APP_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_dir() -> Path:
    """Return the directory used for user-editable configuration files."""
    config_dir = get_user_data_dir() / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_logs_dir() -> Path:
    """Return the directory used for application log files."""
    logs_dir = get_user_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_log_file_path() -> Path:
    """Return the full path to the active log file."""
    return get_logs_dir() / LOG_FILE_NAME


def get_user_settings_path() -> Path:
    """Return the full path to the user's persisted settings file."""
    return get_config_dir() / "user_settings.json"
