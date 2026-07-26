"""
`ConfirmDialog` — a styled modal confirmation dialog that matches
LockIt's dark visual language, replacing bare `QMessageBox.question`
for the overwrite-confirmation prompt in Encrypt/Decrypt pages.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.paths import get_icons_dir
from utils.icon_loader import load_svg_icon


class ConfirmDialog(QDialog):
    """
    Modal confirmation dialog with a title, body message, and two
    labelled action buttons (confirm + cancel).

    Usage::

        dlg = ConfirmDialog(
            parent=self,
            title="Replace existing file?",
            message=f"'{name}' already exists here.\n\nReplacing it is permanent.",
            confirm_label="Replace",
            confirm_is_danger=True,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            ...
    """

    def __init__(
        self,
        *,
        parent: QWidget,
        title: str,
        message: str,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        confirm_is_danger: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(420)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build_ui(title, message, confirm_label, cancel_label, confirm_is_danger)

    def _build_ui(
        self,
        title: str,
        message: str,
        confirm_label: str,
        cancel_label: str,
        confirm_is_danger: bool,
    ) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QWidget(self)
        card.setObjectName("ConfirmCard")
        card.setStyleSheet(
            "#ConfirmCard {"
            "  background-color: #1E1E23;"
            "  border: 1px solid #2E2E35;"
            "  border-radius: 16px;"
            "}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 26, 28, 24)
        card_layout.setSpacing(16)

        # Icon + title row
        header_row = QHBoxLayout()
        header_row.setSpacing(12)
        icons_dir = get_icons_dir()
        icon_label = QLabel(card)
        icon_label.setFixedSize(22, 22)
        icon = load_svg_icon(icons_dir / "info.svg", QColor("#E8B54C"), size=18)
        icon_label.setPixmap(icon.pixmap(18, 18))
        header_row.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        title_label = QLabel(title, card)
        title_label.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #F2F2F5;"
        )
        header_row.addWidget(title_label, stretch=1)
        card_layout.addLayout(header_row)

        # Message
        msg_label = QLabel(message, card)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 13px; color: #B4B4BE; line-height: 160%;")
        card_layout.addWidget(msg_label)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch(1)

        cancel_btn = QPushButton(cancel_label, card)
        cancel_btn.setFixedHeight(38)
        cancel_btn.setMinimumWidth(90)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        confirm_btn = QPushButton(confirm_label, card)
        confirm_btn.setFixedHeight(38)
        confirm_btn.setMinimumWidth(90)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setProperty("variant", "danger" if confirm_is_danger else "primary")
        confirm_btn.clicked.connect(self.accept)
        btn_row.addWidget(confirm_btn)

        card_layout.addLayout(btn_row)
        root.addWidget(card)
