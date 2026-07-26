"""
`ProgressPanel` — a modern, rounded progress indicator with a status
line, percentage, transfer-rate readout, and a cancel button. Designed
to be shown while an encrypt/decrypt worker (Phase 5) runs on a
background thread.
"""

from __future__ import annotations

import time

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget

from ui.styles.theme import ThemeColors
from utils.formatting import format_file_size, format_transfer_rate

_SPEED_SAMPLE_INTERVAL_SECONDS = 0.5


class ProgressPanel(QWidget):
    """Displays progress for a running file operation, with cancellation."""

    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._last_colors: ThemeColors | None = None
        self._start_time: float = 0.0
        self._last_sample_time: float = 0.0
        self._last_sample_bytes: int = 0
        self._current_rate_bytes_per_sec: float = 0.0

        self._build_ui()
        self.reset()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        status_row = QHBoxLayout()
        self._status_label = QLabel("Preparing\u2026", self)
        self._status_label.setProperty("role", "subtitle")
        status_row.addWidget(self._status_label, stretch=1)

        self._percent_label = QLabel("0%", self)
        self._percent_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        status_row.addWidget(self._percent_label)
        layout.addLayout(status_row)

        self._progress_bar = QProgressBar(self)
        self._progress_bar.setRange(0, 1000)  # Fine-grained for smooth animation.
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(10)
        layout.addWidget(self._progress_bar)

        self._value_animation = QPropertyAnimation(self._progress_bar, b"value", self)
        self._value_animation.setDuration(180)
        self._value_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        footer_row = QHBoxLayout()
        self._detail_label = QLabel("", self)
        self._detail_label.setProperty("role", "muted")
        footer_row.addWidget(self._detail_label, stretch=1)

        self._cancel_button = QPushButton("Cancel", self)
        self._cancel_button.setProperty("variant", "danger")
        self._cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_button.setFixedWidth(90)
        self._cancel_button.clicked.connect(self.cancel_requested.emit)
        footer_row.addWidget(self._cancel_button)
        layout.addLayout(footer_row)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset the panel to its initial, pre-operation state."""
        self._start_time = 0.0
        self._last_sample_time = 0.0
        self._last_sample_bytes = 0
        self._current_rate_bytes_per_sec = 0.0
        self._status_label.setText("Preparing\u2026")
        self._percent_label.setText("0%")
        self._detail_label.setText("")
        self._progress_bar.setValue(0)
        self._cancel_button.setEnabled(True)

    def start(self, *, status_text: str = "Processing\u2026") -> None:
        """Mark the operation as started and begin rate tracking."""
        now = time.monotonic()
        self._start_time = now
        self._last_sample_time = now
        self._last_sample_bytes = 0
        self._status_label.setText(status_text)
        self._cancel_button.setEnabled(True)

    def update_progress(self, bytes_processed: int, total_bytes: int) -> None:
        """
        Update the bar, percentage, and transfer-rate readout.

        Intended to be called from the main/UI thread only — Phase 5's
        worker threads emit a Qt signal carrying these values, which a
        slot on `MainWindow` forwards here via a queued connection.
        """
        fraction = 0.0 if total_bytes == 0 else min(bytes_processed / total_bytes, 1.0)
        target_value = round(fraction * 1000)

        self._value_animation.stop()
        self._value_animation.setStartValue(self._progress_bar.value())
        self._value_animation.setEndValue(target_value)
        self._value_animation.start()

        self._percent_label.setText(f"{round(fraction * 100)}%")
        self._update_rate_estimate(bytes_processed)

        processed_display = format_file_size(bytes_processed)
        total_display = format_file_size(total_bytes)
        rate_display = format_transfer_rate(self._current_rate_bytes_per_sec)
        self._detail_label.setText(f"{processed_display} of {total_display} \u00b7 {rate_display}")

    def mark_completed(self, *, success: bool, message: str) -> None:
        """Show a terminal state (success or failure) and disable cancellation."""
        self._status_label.setText(message)
        self._cancel_button.setEnabled(False)
        if success:
            self._progress_bar.setValue(1000)
            self._percent_label.setText("100%")

    def mark_cancelling(self) -> None:
        """Reflect that a cancellation request is being processed."""
        self._status_label.setText("Cancelling\u2026")
        self._cancel_button.setEnabled(False)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _update_rate_estimate(self, bytes_processed: int) -> None:
        now = time.monotonic()
        elapsed = now - self._last_sample_time
        if elapsed >= _SPEED_SAMPLE_INTERVAL_SECONDS:
            delta_bytes = bytes_processed - self._last_sample_bytes
            self._current_rate_bytes_per_sec = delta_bytes / elapsed if elapsed > 0 else 0.0
            self._last_sample_time = now
            self._last_sample_bytes = bytes_processed

    # ------------------------------------------------------------------
    # Theming
    # ------------------------------------------------------------------

    def apply_theme(self, colors: ThemeColors) -> None:
        """Recolor the progress bar track/fill for the active theme."""
        self._last_colors = colors
        self._progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {colors.surface_alt};
                border: none;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {colors.accent};
                border-radius: 5px;
            }}
            """
        )
