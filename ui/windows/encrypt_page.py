"""
`EncryptPage` — the main encrypt interface (Phase 6 revision).

Upgrades from Phase 5:
  - `PasswordStrengthWidget` replaces the old `_StrengthBar` private class
  - `ConfirmDialog` replaces the bare `QMessageBox.question` for overwrite
  - `ToastManager` success/error toasts replace `QMessageBox.critical`
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.files.file_info import suggest_encrypted_output_path
from core.security.password_strength import score_password
from core.validators.exceptions import ValidationError
from core.validators.file_validator import validate_output_path
from ui.dialogs.confirm_dialog import ConfirmDialog
from ui.styles.theme import ThemeColors
from ui.widgets.card import Card
from ui.widgets.drop_zone import DropZone
from ui.widgets.page_header import PageHeader
from ui.widgets.password_strength_widget import PasswordStrengthWidget
from ui.widgets.progress_panel import ProgressPanel
from ui.widgets.toast_manager import ToastManager
from utils.formatting import format_file_size
from utils.logger import get_logger
from workers.crypto_worker import CryptoWorker, OperationKind

logger = get_logger()


class EncryptPage(QScrollArea):
    """Full encrypt workflow page."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._worker: CryptoWorker | None = None
        self._selected_path: Path | None = None
        self._last_colors: ThemeColors | None = None
        self._toast: ToastManager | None = None

        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self._build_ui()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        layout.addWidget(PageHeader(
            "Encrypt File",
            "Protect any file with AES-256 encryption.",
        ))

        # Drop zone
        self._drop_zone = DropZone(
            instruction_text="Drag & drop a file to encrypt",
            browse_button_text="Browse Files",
            icon_file="lock.svg",
        )
        self._drop_zone.file_selected.connect(self._on_file_selected)
        self._drop_zone.selection_cleared.connect(self._on_file_cleared)
        layout.addWidget(self._drop_zone)

        # Password card
        pwd_card = Card()
        pwd_header = QLabel("Encryption Password")
        pwd_header.setStyleSheet("font-weight: 600; font-size: 13px;")
        pwd_card.body_layout.addWidget(pwd_header)

        pwd_row = QHBoxLayout()
        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setPlaceholderText("Enter a strong password\u2026")
        self._password_input.textChanged.connect(self._on_password_changed)
        pwd_row.addWidget(self._password_input)

        self._show_pwd_btn = QPushButton("Show")
        self._show_pwd_btn.setFixedWidth(60)
        self._show_pwd_btn.setCheckable(True)
        self._show_pwd_btn.toggled.connect(self._toggle_password_visibility)
        pwd_row.addWidget(self._show_pwd_btn)
        pwd_card.body_layout.addLayout(pwd_row)

        # New polished strength widget
        self._strength_widget = PasswordStrengthWidget()
        pwd_card.body_layout.addWidget(self._strength_widget)

        layout.addWidget(pwd_card)

        # Encrypt button
        self._encrypt_button = QPushButton("  Encrypt File")
        self._encrypt_button.setProperty("variant", "primary")
        self._encrypt_button.setFixedHeight(46)
        self._encrypt_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._encrypt_button.clicked.connect(self._on_encrypt_clicked)
        self._encrypt_button.setEnabled(False)
        layout.addWidget(self._encrypt_button)

        # Progress panel
        self._progress_card = Card()
        self._progress_panel = ProgressPanel()
        self._progress_panel.cancel_requested.connect(self._on_cancel_requested)
        self._progress_card.body_layout.addWidget(self._progress_panel)
        self._progress_card.setVisible(False)
        layout.addWidget(self._progress_card)

        layout.addStretch(1)
        self.setWidget(container)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_file_selected(self, path: str) -> None:
        self._selected_path = Path(path)
        self._update_encrypt_button_state()

    def _on_file_cleared(self) -> None:
        self._selected_path = None
        self._update_encrypt_button_state()

    def _on_password_changed(self, text: str) -> None:
        if text:
            result = score_password(text)
            self._strength_widget.update_result(result)
        else:
            self._strength_widget.update_result(None)
        self._update_encrypt_button_state()

    def _toggle_password_visibility(self, checked: bool) -> None:
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self._password_input.setEchoMode(mode)
        self._show_pwd_btn.setText("Hide" if checked else "Show")

    def _on_encrypt_clicked(self) -> None:
        if self._selected_path is None:
            return
        password = self._password_input.text()
        output_path = suggest_encrypted_output_path(self._selected_path)
        allow_overwrite = False
        try:
            validate_output_path(output_path, allow_overwrite=False)
        except ValidationError:
            dlg = ConfirmDialog(
                parent=self,
                title="File Already Exists",
                message=f"'{output_path.name}' already exists in this location.\n\nReplacing it is permanent and cannot be undone.",
                confirm_label="Replace",
                confirm_is_danger=True,
            )
            if dlg.exec() != dlg.DialogCode.Accepted:
                return
            allow_overwrite = True
        self._start_worker(password, output_path, allow_overwrite)

    def _on_cancel_requested(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._progress_panel.mark_cancelling()
            self._worker.request_cancel()

    def _on_progress_updated(self, done: int, total: int) -> None:
        self._progress_panel.update_progress(done, total)

    def _on_operation_completed(self, result: object) -> None:
        self._cleanup_worker()
        overhead = result.encrypted_size_bytes - result.original_size_bytes
        overhead_str = f"+{format_file_size(overhead)}" if overhead >= 0 else format_file_size(abs(overhead))
        self._progress_panel.mark_completed(
            success=True,
            message=f"Encrypted in {result.elapsed_seconds:.1f}s \u2014 saved as '{result.output_path.name}'",
        )
        self._encrypt_button.setEnabled(True)
        if self._toast:
            self._toast.success(
                "File Encrypted",
                f"'{result.output_path.name}' saved ({overhead_str} overhead)",
            )

    def _on_operation_failed(self, title: str, detail: str) -> None:
        self._cleanup_worker()
        self._progress_panel.mark_completed(success=False, message=f"{title}: {detail}")
        self._encrypt_button.setEnabled(True)
        if self._toast:
            self._toast.error(title, detail)

    def _on_operation_cancelled(self) -> None:
        self._cleanup_worker()
        self._progress_card.setVisible(False)
        self._encrypt_button.setEnabled(True)
        if self._toast:
            self._toast.info("Cancelled", "The encryption was cancelled.")

    # ------------------------------------------------------------------
    # Worker lifecycle
    # ------------------------------------------------------------------

    def _start_worker(self, password: str, output_path: Path, allow_overwrite: bool) -> None:
        self._encrypt_button.setEnabled(False)
        self._progress_card.setVisible(True)
        self._progress_panel.reset()
        self._progress_panel.start(status_text="Encrypting\u2026")
        self._worker = CryptoWorker(
            kind=OperationKind.ENCRYPT,
            source_path=self._selected_path,
            password=password,
            output_path=output_path,
            allow_overwrite=allow_overwrite,
        )
        self._worker.progress_updated.connect(self._on_progress_updated)
        self._worker.operation_completed.connect(self._on_operation_completed)
        self._worker.operation_failed.connect(self._on_operation_failed)
        self._worker.operation_cancelled.connect(self._on_operation_cancelled)
        self._worker.start()

    def _cleanup_worker(self) -> None:
        if self._worker is not None:
            self._worker.quit()
            self._worker.wait()
            self._worker = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_encrypt_button_state(self) -> None:
        password = self._password_input.text()
        has_file = self._selected_path is not None
        has_password = bool(password) and score_password(password).is_acceptable
        self._encrypt_button.setEnabled(has_file and has_password)

    def set_toast_manager(self, manager: ToastManager) -> None:
        """Called by MainWindow to inject the shared toast manager."""
        self._toast = manager

    def apply_theme(self, colors: ThemeColors) -> None:
        self._last_colors = colors
        self._drop_zone.apply_theme(colors)
        self._progress_panel.apply_theme(colors)
