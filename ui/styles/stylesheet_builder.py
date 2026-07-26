"""
Builds the application-wide QSS stylesheet from a `ThemeColors` palette.

Centralizing style generation here means every widget gets consistent
spacing, radii, and typography automatically, and switching themes is a
single `setStyleSheet` call rather than touching individual widgets.
"""

from __future__ import annotations

from ui.styles.theme import ThemeColors

_FONT_FAMILY = '"Segoe UI", "SF Pro Text", "Inter", "Helvetica Neue", Arial, sans-serif'


def build_stylesheet(colors: ThemeColors) -> str:
    """Generate the full QSS stylesheet for the given color palette."""
    c = colors
    return f"""
    * {{
        font-family: {_FONT_FAMILY};
        outline: none;
    }}

    QMainWindow, QDialog {{
        background-color: {c.background};
    }}

    QWidget {{
        color: {c.text_primary};
        background-color: transparent;
    }}

    QLabel {{
        background-color: transparent;
    }}

    QLabel[role="title"] {{
        font-size: 22px;
        font-weight: 600;
        color: {c.text_primary};
    }}

    QLabel[role="subtitle"] {{
        font-size: 13px;
        color: {c.text_secondary};
        line-height: 150%;
    }}

    QLabel[role="muted"] {{
        font-size: 12px;
        color: {c.text_muted};
    }}

    /* ---------------- Buttons ---------------- */

    QPushButton {{
        background-color: {c.surface};
        border: 1px solid {c.border};
        border-radius: 8px;
        padding: 8px 16px;
        color: {c.text_primary};
        font-size: 13px;
        font-weight: 500;
        min-height: 20px;
    }}

    QPushButton:hover {{
        background-color: {c.surface_hover};
        border-color: {c.scrollbar_handle};
    }}

    QPushButton:pressed {{
        background-color: {c.surface_pressed};
    }}

    QPushButton:disabled {{
        color: {c.text_muted};
        background-color: {c.surface};
        border-color: {c.border_subtle};
    }}

    QPushButton[variant="primary"] {{
        background-color: {c.accent};
        border: 1px solid {c.accent};
        color: {c.text_on_accent};
        font-weight: 600;
        letter-spacing: 0.3px;
    }}

    QPushButton[variant="primary"]:hover {{
        background-color: {c.accent_hover};
        border-color: {c.accent_hover};
    }}

    QPushButton[variant="primary"]:pressed {{
        background-color: {c.accent_pressed};
        border-color: {c.accent_pressed};
    }}

    QPushButton[variant="primary"]:disabled {{
        background-color: {c.surface_alt};
        border-color: {c.surface_alt};
        color: {c.text_muted};
    }}

    QPushButton[variant="danger"] {{
        background-color: transparent;
        border: 1px solid {c.danger};
        color: {c.danger};
    }}

    QPushButton[variant="danger"]:hover {{
        background-color: {c.danger_soft};
    }}

    QPushButton[variant="danger"]:pressed {{
        background-color: {c.danger_soft};
        border-color: {c.danger};
    }}

    /* ---------------- Inputs ---------------- */

    QLineEdit {{
        background-color: {c.surface};
        border: 1px solid {c.border};
        border-radius: 8px;
        padding: 9px 12px;
        color: {c.text_primary};
        font-size: 13px;
        selection-background-color: {c.accent_soft};
        selection-color: {c.text_primary};
        min-height: 20px;
    }}

    QLineEdit:hover {{
        border: 1px solid {c.scrollbar_handle};
    }}

    QLineEdit:focus {{
        border: 1px solid {c.accent};
    }}

    QLineEdit:disabled {{
        color: {c.text_muted};
        background-color: {c.surface_alt};
    }}

    /* ---------------- Cards / Surfaces ---------------- */

    QFrame[role="card"] {{
        background-color: {c.surface};
        border: 1px solid {c.border};
        border-radius: 14px;
    }}

    QFrame[role="separator"] {{
        background-color: {c.border_subtle};
        max-height: 1px;
        min-height: 1px;
    }}

    /* ---------------- Sidebar ---------------- */

    #Sidebar {{
        background-color: {c.sidebar_bg};
        border-right: 1px solid {c.sidebar_border};
    }}

    #SidebarLogoLabel {{
        color: {c.text_primary};
        font-size: 16px;
        font-weight: 700;
    }}

    #SidebarSectionLabel {{
        color: {c.text_muted};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
    }}

    /* ---------------- Scrollbars ---------------- */

    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 4px 2px 4px 0;
    }}

    QScrollBar::handle:vertical {{
        background: {c.scrollbar_handle};
        border-radius: 4px;
        min-height: 24px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {c.scrollbar_handle_hover};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
        margin: 0 4px 2px 4px;
    }}

    QScrollBar::handle:horizontal {{
        background: {c.scrollbar_handle};
        border-radius: 4px;
        min-width: 24px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {c.scrollbar_handle_hover};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ---------------- Tooltips ---------------- */

    QToolTip {{
        background-color: {c.surface};
        color: {c.text_primary};
        border: 1px solid {c.border};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    /* ---------------- QMessageBox (Phase 6) ---------------- */

    QMessageBox {{
        background-color: {c.surface};
    }}

    QMessageBox QLabel {{
        color: {c.text_primary};
        font-size: 13px;
    }}

    /* ---------------- QProgressBar (global fallback) ----------- */

    QProgressBar {{
        background-color: {c.surface_alt};
        border: none;
        border-radius: 5px;
        text-align: center;
        color: transparent;
    }}

    QProgressBar::chunk {{
        background-color: {c.accent};
        border-radius: 5px;
    }}

    /* ---------------- Splitter ---------------- */

    QSplitter::handle {{
        background-color: transparent;
    }}

    /* ---------------- QSlider (Phase 7) ---------------- */

    QSlider::groove:horizontal {{
        background: {c.surface_alt};
        height: 6px;
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: {c.accent};
        border: 2px solid {c.surface};
        width: 18px;
        height: 18px;
        margin: -7px 0;
        border-radius: 9px;
    }}

    QSlider::handle:horizontal:hover {{
        background: {c.accent_hover};
    }}

    QSlider::sub-page:horizontal {{
        background: {c.accent};
        height: 6px;
        border-radius: 3px;
    }}

    /* ---------------- QComboBox (Phase 7) ---------------- */

    QComboBox {{
        background-color: {c.surface};
        border: 1px solid {c.border};
        border-radius: 8px;
        padding: 7px 12px;
        color: {c.text_primary};
        font-size: 13px;
        min-height: 20px;
    }}

    QComboBox:hover {{
        border-color: {c.scrollbar_handle};
    }}

    QComboBox:focus {{
        border-color: {c.accent};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 28px;
    }}

    QComboBox::down-arrow {{
        width: 10px;
        height: 10px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {c.surface};
        border: 1px solid {c.border};
        border-radius: 8px;
        selection-background-color: {c.accent_soft};
        selection-color: {c.text_primary};
        color: {c.text_primary};
        padding: 4px;
        outline: none;
    }}

    QComboBox QAbstractItemView::item {{
        padding: 6px 10px;
        border-radius: 5px;
        min-height: 24px;
    }}

    /* ---------------- QCheckBox (Phase 7) ---------------- */

    QCheckBox {{
        color: {c.text_primary};
        font-size: 13px;
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {c.border};
        border-radius: 5px;
        background: {c.surface};
    }}

    QCheckBox::indicator:hover {{
        border-color: {c.accent};
    }}

    QCheckBox::indicator:checked {{
        background-color: {c.accent};
        border-color: {c.accent};
    }}
    """
