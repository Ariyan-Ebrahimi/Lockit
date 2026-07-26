"""
`SettingsPage` — the full settings interface.

Sections:
  Security   — PBKDF2 iteration count slider with speed/strength labels
  Output     — Where encrypted/decrypted files are saved
  Logging    — Log level; open-log-folder shortcut
  About      — App version; reset to defaults
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config.constants import APP_VERSION
from config.paths import get_logs_dir
from config.settings import (
    ITERATIONS_MAX,
    ITERATIONS_MIN,
    ITERATIONS_STEP,
    AppSettings,
)
from services.settings_service import SettingsService
from ui.styles.theme import ThemeColors
from ui.widgets.page_header import PageHeader
from ui.widgets.settings_widgets import SettingsRow, SettingsSection, SettingsSlider
from ui.widgets.toggle_switch import ToggleSwitch
from ui.widgets.toast_manager import ToastManager
from utils.logger import get_logger

logger = get_logger()

_ITERATIONS_PRESETS = {
    100_000: "100k — Fast (development only)",
    200_000: "200k — Minimum recommended",
    400_000: "400k — Balanced",
    600_000: "600k — Recommended (default)",
    800_000: "800k — Strong",
    1_000_000: "1M — Maximum",
}


def _format_iterations(v: int) -> str:
    """Human-readable iteration count label for the slider."""
    if v >= 1_000_000:
        return f"{v // 1_000_000}M"
    return f"{v // 1_000}k"


class SettingsPage(QScrollArea):
    """Full settings page with live-save behaviour."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._svc = SettingsService.instance()
        self._toast: ToastManager | None = None
        self._inhibit_save = True  # Prevent saves while initialising controls

        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self._build_ui()
        self._load_settings()
        self._inhibit_save = False

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        layout.addWidget(PageHeader(
            "Settings",
            "Changes are saved automatically.",
        ))

        layout.addWidget(self._build_security_section())
        layout.addWidget(self._build_output_section())
        layout.addWidget(self._build_logging_section())
        layout.addWidget(self._build_about_section())
        layout.addStretch(1)
        self.setWidget(container)

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _build_security_section(self) -> QWidget:
        section = SettingsSection("Security")

        self._iterations_slider = SettingsSlider(
            label="Encryption Strength",
            description=(
                "Controls how many PBKDF2 iterations are used to derive your encryption key. "
                "Higher values are slower but much harder to brute-force. "
                "Each file stores its own setting, so changing this only affects new encryptions."
            ),
            minimum=ITERATIONS_MIN,
            maximum=ITERATIONS_MAX,
            step=ITERATIONS_STEP,
            value=self._svc.settings.pbkdf2_iterations,
            format_value=_format_iterations,
        )
        self._iterations_slider.value_changed.connect(self._on_iterations_changed)
        section.add_row(self._iterations_slider)

        # Preset quick-select row
        preset_row_widget = QWidget()
        preset_layout = QHBoxLayout(preset_row_widget)
        preset_layout.setContentsMargins(0, 0, 0, 0)
        preset_layout.setSpacing(8)
        for iterations, label in _ITERATIONS_PRESETS.items():
            btn = QPushButton(label.split(" — ")[0], preset_row_widget)
            btn.setFixedHeight(28)
            btn.setStyleSheet(
                "QPushButton { font-size: 11px; padding: 0 10px; border-radius: 6px; }"
            )
            btn.clicked.connect(
                lambda _, v=iterations: self._iterations_slider.set_value(v)
            )
            preset_layout.addWidget(btn)
        preset_layout.addStretch(1)
        section.add_row(preset_row_widget)

        return section

    def _build_output_section(self) -> QWidget:
        section = SettingsSection("Output Files")

        # Custom output directory toggle
        self._custom_dir_toggle = ToggleSwitch()
        self._custom_dir_toggle.toggled.connect(self._on_custom_dir_toggled)
        section.add_row(SettingsRow(
            label="Save to custom folder",
            description="When off, encrypted/decrypted files are saved next to the source file.",
            control=self._custom_dir_toggle,
        ))

        # Directory picker (shown when toggle is on)
        self._dir_picker_row = QWidget()
        dir_picker_layout = QHBoxLayout(self._dir_picker_row)
        dir_picker_layout.setContentsMargins(0, 0, 0, 0)
        dir_picker_layout.setSpacing(10)

        self._dir_input = QLineEdit()
        self._dir_input.setPlaceholderText("Choose an output folder…")
        self._dir_input.setReadOnly(True)
        dir_picker_layout.addWidget(self._dir_input, stretch=1)

        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._on_browse_output_dir)
        dir_picker_layout.addWidget(browse_btn)

        section.add_row(self._dir_picker_row)
        self._dir_picker_row.setVisible(False)

        return section

    def _build_logging_section(self) -> QWidget:
        section = SettingsSection("Logging")

        # Log level combo
        self._log_level_combo = QComboBox()
        for level in ("DEBUG", "INFO", "WARNING", "ERROR"):
            self._log_level_combo.addItem(level)
        self._log_level_combo.setFixedWidth(120)
        self._log_level_combo.setStyleSheet(self._combo_qss())
        self._log_level_combo.currentTextChanged.connect(self._on_log_level_changed)
        section.add_row(SettingsRow(
            label="Log level",
            description="Controls how much detail is written to the log file.",
            control=self._log_level_combo,
        ))

        # Open logs folder button
        open_logs_btn = QPushButton("Open Logs Folder")
        open_logs_btn.setFixedWidth(150)
        open_logs_btn.clicked.connect(self._open_logs_folder)
        section.add_row(SettingsRow(
            label="Log file location",
            description=str(get_logs_dir()),
            control=open_logs_btn,
        ))

        return section

    def _build_about_section(self) -> QWidget:
        section = SettingsSection("About")

        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet("font-size: 13px; color: #7C7C88; font-weight: 600;")
        section.add_row(SettingsRow(
            label="LockIt",
            description="Secure file encryption built with Python, PySide6, and AES-256.",
            control=version_label,
        ))

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setProperty("variant", "danger")
        reset_btn.setFixedWidth(150)
        reset_btn.clicked.connect(self._on_reset_clicked)
        section.add_row(SettingsRow(
            label="Reset settings",
            description="Restore all settings to their original defaults. Cannot be undone.",
            control=reset_btn,
        ))

        return section

    # ------------------------------------------------------------------
    # Settings load / save
    # ------------------------------------------------------------------

    def _load_settings(self) -> None:
        """Populate all controls from the current AppSettings."""
        s = self._svc.settings

        self._iterations_slider.set_value(s.pbkdf2_iterations)

        self._custom_dir_toggle.set_checked(s.use_custom_output_directory)
        self._dir_picker_row.setVisible(s.use_custom_output_directory)
        if s.custom_output_directory:
            self._dir_input.setText(s.custom_output_directory)

        idx = self._log_level_combo.findText(s.log_level)
        if idx >= 0:
            self._log_level_combo.setCurrentIndex(idx)

    def _save(self, **kwargs) -> None:
        """Apply partial update and persist; no-op during initialisation."""
        if self._inhibit_save:
            return
        self._svc.update(**kwargs)
        logger.debug(f"Settings saved: {kwargs}")

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_iterations_changed(self, value: int) -> None:
        self._save(pbkdf2_iterations=value)

    def _on_custom_dir_toggled(self, checked: bool) -> None:
        self._dir_picker_row.setVisible(checked)
        self._save(use_custom_output_directory=checked)

    def _on_browse_output_dir(self) -> None:
        start = self._dir_input.text() or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(self, "Choose Output Folder", start)
        if chosen:
            self._dir_input.setText(chosen)
            self._save(custom_output_directory=chosen)

    def _on_log_level_changed(self, level: str) -> None:
        self._save(log_level=level)

    def _open_logs_folder(self) -> None:
        logs_dir = str(get_logs_dir())
        try:
            if sys.platform == "win32":
                os.startfile(logs_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", logs_dir])
            else:
                subprocess.Popen(["xdg-open", logs_dir])
        except Exception as exc:
            logger.warning(f"Could not open logs folder: {exc}")
            if self._toast:
                self._toast.error("Could not open folder", str(exc))

    def _on_reset_clicked(self) -> None:
        self._inhibit_save = True
        self._svc.save(AppSettings())
        self._load_settings()
        self._inhibit_save = False
        if self._toast:
            self._toast.info("Settings reset", "All preferences restored to defaults.")
        logger.info("Settings reset to defaults.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_toast_manager(self, manager: ToastManager) -> None:
        self._toast = manager

    def apply_theme(self, colors: ThemeColors) -> None:
        pass  # All colours defined inline against the dark palette.

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _combo_qss() -> str:
        return """
            QComboBox {
                background-color: #1E1E23;
                border: 1px solid #2E2E35;
                border-radius: 8px;
                padding: 6px 10px;
                color: #F2F2F5;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #3A3A42;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E1E23;
                border: 1px solid #2E2E35;
                color: #F2F2F5;
                selection-background-color: #2B2755;
                outline: none;
            }
        """