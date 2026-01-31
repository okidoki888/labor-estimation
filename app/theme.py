# -*- coding: utf-8 -*-
"""
Управление темой оформления (светлая / тёмная)
"""

from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

THEME_KEY = "theme"
THEME_LIGHT = "light"
THEME_DARK = "dark"


def get_theme() -> str:
    """Текущая тема из настроек (по умолчанию светлая)."""
    settings = QSettings()
    return settings.value(THEME_KEY, THEME_LIGHT, type=str)


def set_theme(theme: str) -> None:
    """Сохранить выбор темы в настройки."""
    if theme not in (THEME_LIGHT, THEME_DARK):
        theme = THEME_LIGHT
    settings = QSettings()
    settings.setValue(THEME_KEY, theme)


def get_stylesheet_path(theme: str) -> Path:
    """Путь к файлу стилей для темы."""
    base = Path(__file__).parent / "resources"
    if theme == THEME_DARK:
        return base / "style_dark.qss"
    return base / "style.qss"


def apply_theme(theme: str | None = None) -> None:
    """Применить тему ко всему приложению."""
    if theme is None:
        theme = get_theme()
    path = get_stylesheet_path(theme)
    app = QApplication.instance()
    if app and path.exists():
        with open(path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
