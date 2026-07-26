"""
`SettingsService` — loads and persists `AppSettings` to / from the
platform-appropriate user configuration directory.

Responsibilities:
  - Load settings from JSON on startup (missing file → safe defaults)
  - Validate every field via the Pydantic model on load
  - Write atomically so a crash during save never corrupts the file
  - Notify subscribers via a Qt signal when any setting changes

This is a singleton (accessed via `SettingsService.instance()`) so
every part of the app — pages, workers, future CLI — reads from the
same live configuration object.
"""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from config.paths import get_user_settings_path
from config.settings import AppSettings
from utils.logger import get_logger

logger = get_logger()


class SettingsService(QObject):
    """Singleton that owns the live `AppSettings` and persists changes."""

    settings_changed = Signal(AppSettings)

    _instance: "SettingsService | None" = None

    def __init__(self) -> None:
        super().__init__()
        self._settings: AppSettings = AppSettings()
        self._path: Path = get_user_settings_path()

    @classmethod
    def instance(cls) -> "SettingsService":
        """Return the shared singleton, creating it if needed."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def settings(self) -> AppSettings:
        """The current live settings snapshot (immutable; update via `save`)."""
        return self._settings

    def load(self) -> None:
        """
        Load settings from disk. Safe to call at startup even if the
        file does not yet exist — defaults are used in that case.
        """
        if not self._path.exists():
            logger.info("No settings file found; using defaults.")
            return

        try:
            raw = self._path.read_text(encoding="utf-8")
            data = json.loads(raw)
            self._settings = AppSettings.model_validate(data)
            logger.info(f"Settings loaded from {self._path}")
        except json.JSONDecodeError as exc:
            logger.warning(f"Settings file is malformed ({exc}); using defaults.")
            self._settings = AppSettings()
        except Exception:
            logger.exception("Unexpected error loading settings; using defaults.")
            self._settings = AppSettings()

    def save(self, updated: AppSettings) -> None:
        """
        Persist `updated` to disk atomically and emit `settings_changed`.

        Writes to a `.tmp` file first, then renames it over the real
        file so a crash or power loss during the write can never produce
        a corrupt settings file.
        """
        self._settings = updated
        tmp_path = self._path.with_suffix(".tmp")
        try:
            payload = updated.model_dump_json(indent=2)
            tmp_path.write_text(payload, encoding="utf-8")
            tmp_path.replace(self._path)
            logger.debug("Settings saved.")
        except Exception:
            logger.exception("Failed to save settings.")
            tmp_path.unlink(missing_ok=True)
            raise
        self.settings_changed.emit(self._settings)

    def update(self, **kwargs) -> None:
        """
        Convenience: apply a partial update and save immediately.

        Example::

            SettingsService.instance().update(log_level="DEBUG")
        """
        current = self._settings.model_dump()
        current.update(kwargs)
        self.save(AppSettings.model_validate(current))
