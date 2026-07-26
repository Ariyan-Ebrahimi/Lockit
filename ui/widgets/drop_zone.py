"""
`DropZone` — a combined drag-and-drop target and "Browse" button for
selecting a single input file. Validates the selection immediately via
`core.validators.file_validator` and displays the file's metadata once
accepted.

This widget is self-contained and does not yet perform any
encryption/decryption — Phase 5 ("Integration") connects its
`file_selected` signal to the actual crypto workers.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.paths import get_icons_dir
from core.files.file_info import FileInfo, get_file_info
from core.validators.exceptions import ValidationError
from core.validators.file_validator import validate_input_file
from ui.styles.theme import ThemeColors
from utils.icon_loader import load_svg_icon
from utils.logger import get_logger

logger = get_logger()


class DropZone(QFrame):
    """A dashed-border drop target that also supports browsing for a file."""

    file_selected = Signal(str)  # Emits the validated, resolved file path.
    selection_cleared = Signal()

    def __init__(
        self,
        *,
        instruction_text: str = "Drag & drop a file here",
        browse_button_text: str = "Browse Files",
        file_filter: str = "All Files (*)",
        icon_file: str = "lock.svg",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._file_filter = file_filter
        self._icon_file = icon_file
        self._selected_path: Path | None = None
        self._icons_dir = get_icons_dir()
        self._last_colors: ThemeColors | None = None

        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        self._build_ui(instruction_text, browse_button_text)
        self._show_empty_state()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_ui(self, instruction_text: str, browse_button_text: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon_label = QLabel(self)
        self._icon_label.setFixedSize(40, 40)
        layout.addWidget(self._icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._instruction_label = QLabel(instruction_text, self)
        self._instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._instruction_label.setProperty("role", "subtitle")
        layout.addWidget(self._instruction_label)

        self._or_label = QLabel("or", self)
        self._or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._or_label.setProperty("role", "muted")
        layout.addWidget(self._or_label)

        self._browse_button = QPushButton(browse_button_text, self)
        self._browse_button.setProperty("variant", "primary")
        self._browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._browse_button.setFixedWidth(160)
        self._browse_button.clicked.connect(self._on_browse_clicked)
        layout.addWidget(self._browse_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Selected-file summary row (shown instead of the empty state).
        self._file_row = QWidget(self)
        file_row_layout = QHBoxLayout(self._file_row)
        file_row_layout.setContentsMargins(0, 0, 0, 0)
        file_row_layout.setSpacing(12)

        self._file_icon_label = QLabel(self._file_row)
        self._file_icon_label.setFixedSize(32, 32)
        file_row_layout.addWidget(self._file_icon_label)

        text_column = QVBoxLayout()
        text_column.setSpacing(2)
        self._file_name_label = QLabel(self._file_row)
        self._file_name_label.setProperty("role", "title")
        self._file_name_label.setStyleSheet("font-size: 15px; font-weight: 600;")
        self._file_meta_label = QLabel(self._file_row)
        self._file_meta_label.setProperty("role", "muted")
        text_column.addWidget(self._file_name_label)
        text_column.addWidget(self._file_meta_label)
        file_row_layout.addLayout(text_column, stretch=1)

        self._clear_button = QPushButton("Change File", self._file_row)
        self._clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_button.clicked.connect(self.clear_selection)
        file_row_layout.addWidget(self._clear_button)

        layout.addWidget(self._file_row)

        self._error_label = QLabel(self)
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

    # ------------------------------------------------------------------
    # State rendering
    # ------------------------------------------------------------------

    def _show_empty_state(self) -> None:
        self._instruction_label.setVisible(True)
        self._or_label.setVisible(True)
        self._browse_button.setVisible(True)
        self._file_row.setVisible(False)
        self._icon_label.setVisible(True)

    def _show_selected_state(self, info: FileInfo) -> None:
        self._instruction_label.setVisible(False)
        self._or_label.setVisible(False)
        self._browse_button.setVisible(False)
        self._icon_label.setVisible(False)
        self._file_row.setVisible(True)
        self._error_label.setVisible(False)

        self._file_name_label.setText(info.name)
        self._file_meta_label.setText(f"{info.size_display} \u00b7 modified {info.modified_display}")

        if self._last_colors is not None:
            icon = load_svg_icon(
                self._icons_dir / self._icon_file, QColor(self._last_colors.accent), size=28
            )
            self._file_icon_label.setPixmap(icon.pixmap(28, 28))

    def _show_error(self, message: str) -> None:
        self._error_label.setText(message)
        self._error_label.setVisible(True)

    # ------------------------------------------------------------------
    # Selection handling
    # ------------------------------------------------------------------

    def _try_select_file(self, raw_path: str) -> None:
        try:
            validated_path = validate_input_file(raw_path)
        except ValidationError as exc:
            logger.debug(f"Rejected file selection: {exc}")
            self._show_error(str(exc))
            return

        info = get_file_info(validated_path)
        self._selected_path = validated_path
        self._show_selected_state(info)
        self.file_selected.emit(str(validated_path))
        logger.info(f"File selected: {validated_path.name} ({info.size_display})")

    def clear_selection(self) -> None:
        """Reset the widget back to its empty drag-and-drop state."""
        self._selected_path = None
        self._show_empty_state()
        self.selection_cleared.emit()

    @property
    def selected_path(self) -> Path | None:
        return self._selected_path

    def _on_browse_clicked(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(self, "Select a file", "", self._file_filter)
        if path_str:
            self._try_select_file(path_str)

    # ------------------------------------------------------------------
    # Drag & drop events
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
            event.acceptProposedAction()
            self.setProperty("dragActive", True)
            self._refresh_style()
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        self.setProperty("dragActive", False)
        self._refresh_style()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        self.setProperty("dragActive", False)
        self._refresh_style()

        urls = event.mimeData().urls()
        if len(urls) != 1:
            self._show_error("Please drop exactly one file.")
            return

        local_path = urls[0].toLocalFile()
        if not local_path:
            self._show_error("That doesn't look like a local file.")
            return

        event.acceptProposedAction()
        self._try_select_file(local_path)

    def _refresh_style(self) -> None:
        self.style().unpolish(self)
        self.style().polish(self)

    # ------------------------------------------------------------------
    # Theming
    # ------------------------------------------------------------------

    def apply_theme(self, colors: ThemeColors) -> None:
        """Recolor icons and the dashed border for the active theme."""
        self._last_colors = colors

        icon = load_svg_icon(self._icons_dir / self._icon_file, QColor(colors.text_muted), size=36)
        self._icon_label.setPixmap(icon.pixmap(36, 36))

        if self._selected_path is not None:
            icon = load_svg_icon(self._icons_dir / self._icon_file, QColor(colors.accent), size=28)
            self._file_icon_label.setPixmap(icon.pixmap(28, 28))

        self._error_label.setStyleSheet(f"color: {colors.danger}; font-size: 12px;")
        self._clear_button.setStyleSheet(
            f"""
            QPushButton {{
                border: none;
                background: transparent;
                color: {colors.accent};
                font-weight: 600;
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {colors.accent_soft};
                color: {colors.accent_hover};
            }}
            QPushButton:pressed {{
                background: {colors.accent_soft};
                color: {colors.accent_pressed};
            }}
            """
        )

        self.setStyleSheet(
            f"""
            DropZone {{
                background-color: {colors.surface_alt};
                border: 2px dashed {colors.border};
                border-radius: 16px;
            }}
            DropZone:hover {{
                background-color: {colors.surface_hover};
                border: 2px dashed {colors.scrollbar_handle};
            }}
            DropZone[dragActive="true"] {{
                background-color: {colors.accent_soft};
                border: 2px dashed {colors.accent};
            }}
            """
        )
