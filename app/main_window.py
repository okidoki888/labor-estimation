# -*- coding: utf-8 -*-
"""
Главное окно приложения «Расчёт трудоёмкости разработки ПС»
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QMenu, QStatusBar,
    QFileDialog, QMessageBox, QApplication, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence, QCloseEvent, QFont, QResizeEvent

from .models.project import Project
from .models.calculation import CalculationEngine, CalculationResult
from .widgets.project_info import ProjectInfoWidget
from .widgets.components_editor import ComponentsEditorWidget
from .widgets.coefficients_panel import CoefficientsPanelWidget
from .widgets.results_view import ResultsViewWidget


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    project_changed = Signal()
    calculation_updated = Signal(CalculationResult)

    def __init__(self):
        super().__init__()
        self.project = Project()
        self.calculation_result: Optional[CalculationResult] = None
        self.autosave_path: Optional[str] = None

        # Опорная ширина для масштабирования шрифтов (при этой ширине базовый размер)
        self._font_scale_reference_width = 1200
        self._font_base_point_size = 12
        self._font_min_point_size = 10
        self._font_max_point_size = 16
        self._last_applied_scale = 1.0
        self._font_scale_timer = QTimer(self)
        self._font_scale_timer.setSingleShot(True)
        self._font_scale_timer.timeout.connect(self._apply_font_scale)

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._setup_autosave()
        self._connect_signals()

        self.setWindowTitle("Расчёт трудоёмкости разработки ПС — Новый проект")
        self.resize(1200, 800)
        self._apply_font_scale()

    def _setup_ui(self):
        """Настройка интерфейса"""
        # Главный виджет с вкладками
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Вкладка 1: Общие сведения
        self.project_info = ProjectInfoWidget(self.project)
        self.tabs.addTab(self.project_info, "Общие сведения")

        # Вкладка 2: Каталог функций
        self.components_editor = ComponentsEditorWidget(self.project)
        self.tabs.addTab(self.components_editor, "Каталог функций")

        # Вкладка 3: Коэффициенты
        self.coefficients_panel = CoefficientsPanelWidget(self.project)
        self.tabs.addTab(self.coefficients_panel, "Коэффициенты")

        # Вкладка 4: Результаты расчёта
        self.results_view = ResultsViewWidget()
        self.tabs.addTab(self.results_view, "Результаты расчёта")

        # Вкладка 5: Экспорт (будет реализована позже)
        self.export_tab = self._create_export_tab()
        self.tabs.addTab(self.export_tab, "Экспорт")

    def _create_export_tab(self) -> QWidget:
        """Создание вкладки экспорта"""
        from PySide6.QtWidgets import QPushButton, QGroupBox, QHBoxLayout, QLabel

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Группа экспорта в файлы
        export_group = QGroupBox("Экспорт результатов")
        export_layout = QVBoxLayout(export_group)

        # Кнопка экспорта в Word
        self.btn_export_word = QPushButton("Экспорт в Word (.docx)")
        self.btn_export_word.setMinimumHeight(40)
        self.btn_export_word.clicked.connect(self._export_to_word)
        export_layout.addWidget(self.btn_export_word)

        # Кнопка экспорта в Excel
        self.btn_export_excel = QPushButton("Экспорт в Excel (.xlsx)")
        self.btn_export_excel.setMinimumHeight(40)
        self.btn_export_excel.clicked.connect(self._export_to_excel)
        export_layout.addWidget(self.btn_export_excel)

        layout.addWidget(export_group)

        # Группа сохранения проекта
        project_group = QGroupBox("Проект")
        project_layout = QVBoxLayout(project_group)

        self.btn_save_project = QPushButton("Сохранить проект")
        self.btn_save_project.setMinimumHeight(40)
        self.btn_save_project.clicked.connect(self._save_project)
        project_layout.addWidget(self.btn_save_project)

        self.btn_load_project = QPushButton("Загрузить проект")
        self.btn_load_project.setMinimumHeight(40)
        self.btn_load_project.clicked.connect(self._open_project)
        project_layout.addWidget(self.btn_load_project)

        layout.addWidget(project_group)

        # Информация
        info_label = QLabel(
            "Для экспорта сначала выполните расчёт на вкладке «Результаты расчёта»"
        )
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)

        layout.addStretch()
        return widget

    def _setup_menu(self):
        """Настройка меню"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")

        new_action = QAction("Новый проект", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)

        open_action = QAction("Открыть проект...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)

        save_action = QAction("Сохранить", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction("Сохранить как...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        load_example = QAction("Загрузить пример из методики", self)
        load_example.triggered.connect(self._load_example)
        file_menu.addAction(load_example)

        file_menu.addSeparator()

        export_word = QAction("Экспорт в Word...", self)
        export_word.setShortcut(QKeySequence("Ctrl+E"))
        export_word.triggered.connect(self._export_to_word)
        file_menu.addAction(export_word)

        export_excel = QAction("Экспорт в Excel...", self)
        export_excel.triggered.connect(self._export_to_excel)
        file_menu.addAction(export_excel)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Расчёт
        calc_menu = menubar.addMenu("Расчёт")

        calc_action = QAction("Выполнить расчёт", self)
        calc_action.setShortcut(QKeySequence("F5"))
        calc_action.triggered.connect(self._calculate)
        calc_menu.addAction(calc_action)

        # Меню Вид — смена темы
        view_menu = menubar.addMenu("Вид")
        from .theme import get_theme, set_theme, apply_theme, THEME_LIGHT, THEME_DARK

        self.action_theme_light = QAction("Светлая тема", self)
        self.action_theme_light.setCheckable(True)
        self.action_theme_light.triggered.connect(lambda: self._switch_theme(THEME_LIGHT))
        view_menu.addAction(self.action_theme_light)

        self.action_theme_dark = QAction("Тёмная тема", self)
        self.action_theme_dark.setCheckable(True)
        self.action_theme_dark.triggered.connect(lambda: self._switch_theme(THEME_DARK))
        view_menu.addAction(self.action_theme_dark)

        current = get_theme()
        self.action_theme_light.setChecked(current == THEME_LIGHT)
        self.action_theme_dark.setChecked(current == THEME_DARK)

        # Меню Справка
        help_menu = menubar.addMenu("Справка")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self):
        """Настройка строки состояния"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self._update_statusbar()

    def _setup_autosave(self):
        """Настройка автосохранения"""
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.start(5 * 60 * 1000)  # 5 минут

    def _connect_signals(self):
        """Подключение сигналов"""
        self.project_info.data_changed.connect(self._on_project_changed)
        self.components_editor.data_changed.connect(self._on_project_changed)
        self.coefficients_panel.data_changed.connect(self._on_project_changed)
        self.results_view.calculate_requested.connect(self._calculate)

    def _on_project_changed(self):
        """Обработка изменения проекта"""
        self.project.modified = True
        self._update_title()
        self._update_statusbar()

    def _update_title(self):
        """Обновление заголовка окна"""
        title = f"Расчёт трудоёмкости разработки ПС — {self.project.name}"
        if self.project.modified:
            title += " *"
        self.setWindowTitle(title)

    def _update_statusbar(self):
        """Обновление строки состояния"""
        volume = self.project.get_total_volume()
        func_count = self.project.get_function_count()
        comp_count = len(self.project.components)

        status = f"Компонентов: {comp_count} | Функций: {func_count} | Базовый объём: {volume} строк"

        if self.calculation_result:
            status += f" | Расчёт выполнен: T = {self.calculation_result.total_labor} чел.-дн."

        self.statusbar.showMessage(status)

    def _new_project(self):
        """Создание нового проекта"""
        if self.project.modified:
            reply = QMessageBox.question(
                self, "Сохранить изменения?",
                "Проект был изменён. Сохранить перед созданием нового?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                if not self._save_project():
                    return
            elif reply == QMessageBox.Cancel:
                return

        self.project = Project()
        self.calculation_result = None
        self._refresh_all_widgets()
        self._update_title()
        self._update_statusbar()

    def _open_project(self):
        """Открытие проекта"""
        if self.project.modified:
            reply = QMessageBox.question(
                self, "Сохранить изменения?",
                "Проект был изменён. Сохранить перед открытием другого?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                if not self._save_project():
                    return
            elif reply == QMessageBox.Cancel:
                return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть проект",
            "", "Проекты расчёта (*.json);;Все файлы (*)"
        )
        if file_path:
            try:
                self.project = Project.load(file_path)
                self.calculation_result = None
                self._refresh_all_widgets()
                self._update_title()
                self._update_statusbar()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить проект:\n{e}")

    def _save_project(self) -> bool:
        """Сохранение проекта"""
        if not self.project.file_path:
            return self._save_project_as()

        try:
            self.project.save()
            self._update_title()
            self.statusbar.showMessage("Проект сохранён", 3000)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить проект:\n{e}")
            return False

    def _save_project_as(self) -> bool:
        """Сохранение проекта с выбором файла"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить проект как",
            f"{self.project.name}.json",
            "Проекты расчёта (*.json);;Все файлы (*)"
        )
        if file_path:
            try:
                self.project.save(file_path)
                self._update_title()
                self.statusbar.showMessage("Проект сохранён", 3000)
                return True
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить проект:\n{e}")
        return False

    def _load_example(self):
        """Загрузка эталонного примера"""
        if self.project.modified:
            reply = QMessageBox.question(
                self, "Сохранить изменения?",
                "Проект был изменён. Сохранить перед загрузкой примера?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                if not self._save_project():
                    return
            elif reply == QMessageBox.Cancel:
                return

        self.project = Project.create_example()
        self.calculation_result = None
        self._refresh_all_widgets()
        self._update_title()
        self._update_statusbar()
        self.statusbar.showMessage("Загружен эталонный пример из методики", 3000)

    def _calculate(self):
        """Выполнение расчёта"""
        if not self.project.components:
            QMessageBox.warning(self, "Предупреждение", "Добавьте хотя бы один компонент с функциями")
            return

        if self.project.get_function_count() == 0:
            QMessageBox.warning(self, "Предупреждение", "Добавьте хотя бы одну функцию")
            return

        engine = CalculationEngine()
        self.calculation_result = engine.calculate(self.project)

        self.results_view.update_results(self.calculation_result, self.project)
        self.tabs.setCurrentWidget(self.results_view)
        self._update_statusbar()
        self.statusbar.showMessage("Расчёт выполнен", 3000)

    def _export_to_word(self):
        """Экспорт в Word"""
        if not self.calculation_result:
            QMessageBox.warning(self, "Предупреждение", "Сначала выполните расчёт")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в Word",
            f"{self.project.name}.docx",
            "Документ Word (*.docx)"
        )
        if file_path:
            try:
                from .export.docx_export import export_to_docx
                export_to_docx(self.project, self.calculation_result, file_path)
                self.statusbar.showMessage(f"Экспортировано в {file_path}", 3000)
                QMessageBox.information(self, "Экспорт завершён", f"Отчёт сохранён в:\n{file_path}")
            except ImportError:
                QMessageBox.warning(self, "Ошибка", "Модуль python-docx не установлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{e}")

    def _export_to_excel(self):
        """Экспорт в Excel"""
        if not self.calculation_result:
            QMessageBox.warning(self, "Предупреждение", "Сначала выполните расчёт")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в Excel",
            f"{self.project.name}.xlsx",
            "Книга Excel (*.xlsx)"
        )
        if file_path:
            try:
                from .export.xlsx_export import export_to_xlsx
                export_to_xlsx(self.project, self.calculation_result, file_path)
                self.statusbar.showMessage(f"Экспортировано в {file_path}", 3000)
                QMessageBox.information(self, "Экспорт завершён", f"Книга сохранена в:\n{file_path}")
            except ImportError:
                QMessageBox.warning(self, "Ошибка", "Модуль openpyxl не установлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{e}")

    def _autosave(self):
        """Автосохранение во временный файл"""
        if self.project.modified:
            try:
                if not self.autosave_path:
                    fd, self.autosave_path = tempfile.mkstemp(suffix=".json", prefix="labor_autosave_")
                    os.close(fd)
                self.project.save(self.autosave_path)
            except Exception:
                pass  # Игнорируем ошибки автосохранения

    def _switch_theme(self, theme: str):
        """Переключение темы оформления"""
        from .theme import set_theme, apply_theme, THEME_LIGHT, THEME_DARK

        set_theme(theme)
        apply_theme(theme)
        self.action_theme_light.setChecked(theme == THEME_LIGHT)
        self.action_theme_dark.setChecked(theme == THEME_DARK)
        self.statusbar.showMessage("Тема изменена", 2000)

    def _show_about(self):
        """Показ информации о программе"""
        QMessageBox.about(
            self, "О программе",
            "<h3>Расчёт трудоёмкости разработки ПС</h3>"
            "<p>Версия 1.0.0</p>"
            "<p>Приложение для расчёта трудоёмкости разработки "
            "программных средств по методике СПбГУТ "
            "им. проф. М.А. Бонч-Бруевича.</p>"
            "<p>Кафедра Информационных управляющих систем</p>"
        )

    def _refresh_all_widgets(self):
        """Обновление всех виджетов после загрузки проекта"""
        self.project_info.set_project(self.project)
        self.components_editor.set_project(self.project)
        self.coefficients_panel.set_project(self.project)
        self.results_view.clear()

    def resizeEvent(self, event: QResizeEvent):
        """При изменении размера окна — отложенная подстройка шрифта."""
        super().resizeEvent(event)
        self._font_scale_timer.stop()
        self._font_scale_timer.start(80)

    def _apply_font_scale(self):
        """Подстроить размер шрифта приложения под ширину окна."""
        app = QApplication.instance()
        if not app:
            return
        w = self.width()
        if w <= 0:
            return
        scale = w / self._font_scale_reference_width
        scale = max(0.75, min(1.35, scale))
        if abs(scale - self._last_applied_scale) < 0.02:
            return
        self._last_applied_scale = scale
        point_size = max(
            self._font_min_point_size,
            min(self._font_max_point_size, round(self._font_base_point_size * scale))
        )
        font = app.font()
        font.setPointSize(point_size)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        app.setFont(font)

    def closeEvent(self, event: QCloseEvent):
        """Обработка закрытия окна"""
        if self.project.modified:
            reply = QMessageBox.question(
                self, "Сохранить изменения?",
                "Проект был изменён. Сохранить перед выходом?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                if not self._save_project():
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        # Удаляем временный файл автосохранения
        if self.autosave_path and os.path.exists(self.autosave_path):
            try:
                os.unlink(self.autosave_path)
            except Exception:
                pass

        event.accept()
