"""
SVG icon loading with theme-aware color tinting.

QIcon does not natively support recoloring an SVG that uses
`stroke="currentColor"` based on a QSS/theme color. This module renders
each SVG onto a transparent QPixmap at the requested size and then tints
it using `QPainter.CompositionMode_SourceIn`, so the same source icon can
be rendered in any color for light mode, dark mode, hover states, or
disabled states.

Rendered pixmaps are cached per (path, color, size) to avoid repeated
disk reads and rasterization.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_pixmap_cache: dict[tuple[str, str, int, int], QPixmap] = {}


def _render_tinted_pixmap(svg_path: Path, color: QColor, size: QSize) -> QPixmap:
    """Render an SVG file to a QPixmap tinted with the given color."""
    cache_key = (str(svg_path), color.name(QColor.NameFormat.HexArgb), size.width(), size.height())
    cached = _pixmap_cache.get(cache_key)
    if cached is not None:
        return cached

    if not svg_path.is_file():
        return QPixmap()

    renderer = QSvgRenderer(str(svg_path))
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
    finally:
        painter.end()

    _pixmap_cache[cache_key] = pixmap
    return pixmap


def load_svg_icon(svg_path: Path, color: QColor, size: int = 20) -> QIcon:
    """
    Load an SVG file as a QIcon tinted with the given color.

    Args:
        svg_path: Path to the source `.svg` file.
        color: Color to tint the icon with (theme-dependent).
        size: Square pixel size to render at (uses device pixel ratio 2x
              internally for crisp rendering on high-DPI displays).

    Returns:
        A QIcon ready to use on buttons, labels, or menus.
    """
    render_size = QSize(size * 2, size * 2)
    pixmap = _render_tinted_pixmap(svg_path, color, render_size)
    pixmap.setDevicePixelRatio(2.0)
    return QIcon(pixmap)


def clear_icon_cache() -> None:
    """Clear the rendered-icon cache. Useful in tests."""
    _pixmap_cache.clear()
