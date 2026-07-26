"""
Reusable building-block widgets for the Settings page.

`SettingsSection`  — a titled card grouping related settings rows.
`SettingsRow`      — a label (left) + any control widget (right) row.
`SettingsSlider`   — a row with a QSlider, live value label, and description.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ui.styles.theme import ThemeColors


class SettingsSection(QFrame):
    """A titled card that groups related settings rows."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("role", "card")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(0)

        title_label = QLabel(title, self)
        title_label.setStyleSheet(
            "font-size: 11px; font-weight: 700; letter-spacing: 0.8px;"
            " color: #7C7C88; text-transform: uppercase;"
        )
        outer.addWidget(title_label)
        outer.addSpacing(14)

        self._rows_widget = QWidget(self)
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(0)
        outer.addWidget(self._rows_widget)

    def add_row(self, row: QWidget) -> None:
        """Append a row (SettingsRow or any widget) to this section."""
        if self._rows_layout.count() > 0:
            sep = QFrame(self._rows_widget)
            sep.setProperty("role", "separator")
            sep.setFixedHeight(1)
            self._rows_layout.addSpacing(12)
            self._rows_layout.addWidget(sep)
            self._rows_layout.addSpacing(12)
        self._rows_layout.addWidget(row)


class SettingsRow(QWidget):
    """A label/description on the left and a control widget on the right."""

    def __init__(
        self,
        *,
        label: str,
        description: str = "",
        control: QWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(16)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        label_widget = QLabel(label, self)
        label_widget.setStyleSheet("font-size: 13px; font-weight: 500; color: #F2F2F5;")
        text_col.addWidget(label_widget)

        if description:
            desc_widget = QLabel(description, self)
            desc_widget.setWordWrap(True)
            desc_widget.setStyleSheet("font-size: 11px; color: #7C7C88;")
            text_col.addWidget(desc_widget)

        layout.addLayout(text_col, stretch=1)
        layout.addWidget(control, alignment=Qt.AlignmentFlag.AlignVCenter)


class SettingsSlider(QWidget):
    """A full-width row with label, description, slider, and value display."""

    value_changed = Signal(int)

    def __init__(
        self,
        *,
        label: str,
        description: str = "",
        minimum: int,
        maximum: int,
        step: int,
        value: int,
        format_value: "callable[[int], str] | None" = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._format_value = format_value or (lambda v: str(v))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)

        # Header row: label (left) + current value (right)
        header = QHBoxLayout()
        label_widget = QLabel(label, self)
        label_widget.setStyleSheet("font-size: 13px; font-weight: 500; color: #F2F2F5;")
        header.addWidget(label_widget, stretch=1)

        self._value_label = QLabel(self._format_value(value), self)
        self._value_label.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #8577F0;"
        )
        header.addWidget(self._value_label)
        layout.addLayout(header)

        # Description
        if description:
            desc_widget = QLabel(description, self)
            desc_widget.setWordWrap(True)
            desc_widget.setStyleSheet("font-size: 11px; color: #7C7C88;")
            layout.addWidget(desc_widget)

        # Slider
        self._slider = QSlider(Qt.Orientation.Horizontal, self)
        self._slider.setMinimum(minimum)
        self._slider.setMaximum(maximum)
        self._slider.setSingleStep(step)
        self._slider.setPageStep(step * 2)
        self._slider.setTickInterval(step)
        self._slider.setValue(value)
        self._slider.valueChanged.connect(self._on_slider_changed)
        self._slider.setStyleSheet(self._slider_qss())
        layout.addWidget(self._slider)

        # Min / max labels
        minmax = QHBoxLayout()
        min_lbl = QLabel(self._format_value(minimum), self)
        min_lbl.setStyleSheet("font-size: 10px; color: #7C7C88;")
        max_lbl = QLabel(self._format_value(maximum), self)
        max_lbl.setStyleSheet("font-size: 10px; color: #7C7C88;")
        max_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        minmax.addWidget(min_lbl)
        minmax.addStretch(1)
        minmax.addWidget(max_lbl)
        layout.addLayout(minmax)

    def get_value(self) -> int:
        return self._slider.value()

    def set_value(self, value: int) -> None:
        self._slider.setValue(value)

    def _on_slider_changed(self, value: int) -> None:
        # Snap to nearest step
        step = self._slider.singleStep()
        snapped = round(value / step) * step
        if snapped != value:
            self._slider.setValue(snapped)
            return
        self._value_label.setText(self._format_value(value))
        self.value_changed.emit(value)

    @staticmethod
    def _slider_qss() -> str:
        return """
            QSlider::groove:horizontal {
                height: 4px;
                background: #2E2E35;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #8577F0;
                border: 2px solid #1E1E23;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -7px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #9A8EF5;
            }
            QSlider::sub-page:horizontal {
                background: #8577F0;
                border-radius: 2px;
            }
        """

    def apply_theme(self, colors: ThemeColors) -> None:
        pass  # Colours are hardcoded to dark palette; here for interface consistency.
