"""
Theme definitions for LockIt.

Defines the set of design tokens (colors) that every visual surface in
the application draws from, plus the light and dark palettes. Keeping
colors as named tokens (rather than hardcoding hex values throughout the
UI) is what allows instant, consistent theme switching.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ThemeMode(str, Enum):
    """
    Theme preference. LockIt is dark-only: DARK is the sole supported
    value, kept as an enum (rather than removed outright) so the rest of
    the theming plumbing (ThemeManager, signals, palette lookup) doesn't
    need to change shape if a light theme is ever reintroduced.
    """

    DARK = "dark"


@dataclass(frozen=True, slots=True)
class ThemeColors:
    """A complete set of color tokens for one theme variant."""

    # Surfaces
    background: str
    surface: str
    surface_alt: str
    surface_hover: str
    surface_pressed: str
    border: str
    border_subtle: str

    # Text
    text_primary: str
    text_secondary: str
    text_muted: str
    text_on_accent: str

    # Brand / accent
    accent: str
    accent_hover: str
    accent_pressed: str
    accent_soft: str

    # Semantic
    success: str
    warning: str
    danger: str
    danger_soft: str

    # Sidebar (distinct surface from main content)
    sidebar_bg: str
    sidebar_text: str
    sidebar_text_active: str
    sidebar_hover: str
    sidebar_active_bg: str
    sidebar_border: str

    # Scrollbar
    scrollbar_handle: str
    scrollbar_handle_hover: str


DARK_COLORS = ThemeColors(
    background="#17171B",
    surface="#1E1E23",
    surface_alt="#232329",
    surface_hover="#2C2C34",
    surface_pressed="#34343D",
    border="#2E2E35",
    border_subtle="#28282E",
    text_primary="#F2F2F5",
    text_secondary="#B4B4BE",
    text_muted="#7C7C88",
    text_on_accent="#FFFFFF",
    accent="#8577F0",
    accent_hover="#9A8EF5",
    accent_pressed="#7466E0",
    accent_soft="#2B2755",
    success="#3DC98A",
    warning="#E8B54C",
    danger="#F0666B",
    danger_soft="#3A2226",
    sidebar_bg="#1B1B20",
    sidebar_text="#B4B4BE",
    sidebar_text_active="#F2F2F5",
    sidebar_hover="#28282F",
    sidebar_active_bg="#2B2755",
    sidebar_border="#2E2E35",
    scrollbar_handle="#3A3A42",
    scrollbar_handle_hover="#4A4A54",
)


def get_palette(mode: ThemeMode = ThemeMode.DARK) -> ThemeColors:
    """Return the color palette. LockIt only ships a dark palette."""
    return DARK_COLORS
