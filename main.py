#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расчёт трудоёмкости разработки ПС
по методике СПбГУТ им. проф. М.А. Бонч-Бруевича

Точка входа в приложение
"""

import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.main_window import MainWindow


def main():
    """Главная функция приложения"""
    # Создаём приложение
    app = QApplication(sys.argv)

    # Настройка приложения
    app.setApplicationName("Расчёт трудоёмкости разработки ПС")
    app.setOrganizationName("СПбГУТ")
    app.setOrganizationDomain("sut.ru")

    # Шрифт по умолчанию (системный стек, читаемый размер)
    font = QFont()
    font.setPointSize(12)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # Стиль Fusion + тема (светлая/тёмная из настроек)
    app.setStyle("Fusion")
    from app.theme import get_theme, apply_theme
    apply_theme(get_theme())

    # Создаём и показываем главное окно
    window = MainWindow()
    window.show()

    # Запускаем цикл обработки событий
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
