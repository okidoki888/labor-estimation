# -*- coding: utf-8 -*-
"""
Виджет общих сведений о проекте (Вкладка 1)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QGroupBox
)
from PySide6.QtCore import Signal

from ..models.project import Project


class ProjectInfoWidget(QWidget):
    """Виджет для ввода общих сведений о ПС"""

    data_changed = Signal()

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self._updating = False
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Группа: Сведения о ПС
        info_group = QGroupBox("Сведения о программном средстве")
        info_layout = QFormLayout(info_group)

        # Название ПС
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название программного средства")
        self.name_edit.textChanged.connect(self._on_name_changed)
        info_layout.addRow("Название ПС:", self.name_edit)

        # Описание
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Краткое описание программного средства")
        self.description_edit.setMaximumHeight(80)
        self.description_edit.textChanged.connect(self._on_description_changed)
        info_layout.addRow("Описание:", self.description_edit)

        layout.addWidget(info_group)

        # Группа: Параметры расчёта
        params_group = QGroupBox("Параметры расчёта")
        params_layout = QFormLayout(params_group)

        # Фонд рабочего времени
        self.work_fund_spin = QSpinBox()
        self.work_fund_spin.setRange(1, 31)
        self.work_fund_spin.setValue(21)
        self.work_fund_spin.setSuffix(" дней/месяц")
        self.work_fund_spin.setToolTip("Количество рабочих дней в месяце (по умолчанию 21)")
        self.work_fund_spin.valueChanged.connect(self._on_work_fund_changed)
        params_layout.addRow("Фонд рабочего времени:", self.work_fund_spin)

        # Тип ограничения
        constraint_layout = QHBoxLayout()

        self.constraint_type_combo = QComboBox()
        self.constraint_type_combo.addItems([
            "По продолжительности",
            "По численности"
        ])
        self.constraint_type_combo.setToolTip(
            "Выберите тип ограничения:\n"
            "- По продолжительности: задаётся срок, рассчитывается численность\n"
            "- По численности: задаётся число исполнителей, рассчитывается срок"
        )
        self.constraint_type_combo.currentIndexChanged.connect(self._on_constraint_type_changed)
        constraint_layout.addWidget(self.constraint_type_combo)

        self.constraint_value_spin = QDoubleSpinBox()
        self.constraint_value_spin.setRange(0.1, 1000)
        self.constraint_value_spin.setValue(12.0)
        self.constraint_value_spin.setDecimals(1)
        self.constraint_value_spin.valueChanged.connect(self._on_constraint_value_changed)
        constraint_layout.addWidget(self.constraint_value_spin)

        self.constraint_unit_label = QLabel("месяцев")
        constraint_layout.addWidget(self.constraint_unit_label)

        params_layout.addRow("Ограничение:", constraint_layout)

        layout.addWidget(params_group)

        # Информационная панель
        info_panel = QGroupBox("Справка")
        info_panel_layout = QVBoxLayout(info_panel)

        info_text = QLabel(
            "<p><b>Порядок работы:</b></p>"
            "<ol>"
            "<li>Заполните общие сведения о ПС</li>"
            "<li>На вкладке «Каталог функций» создайте компоненты и добавьте функции</li>"
            "<li>На вкладке «Коэффициенты» выберите значения коэффициентов</li>"
            "<li>На вкладке «Результаты расчёта» нажмите «Рассчитать»</li>"
            "<li>Экспортируйте результаты в Word или Excel</li>"
            "</ol>"
            "<p><b>Методика:</b> СПбГУТ им. проф. М.А. Бонч-Бруевича</p>"
        )
        info_text.setWordWrap(True)
        info_panel_layout.addWidget(info_text)

        layout.addWidget(info_panel)

        layout.addStretch()

    def _load_data(self):
        """Загрузка данных из проекта"""
        self._updating = True
        self.name_edit.setText(self.project.name)
        self.description_edit.setPlainText(self.project.description)
        self.work_fund_spin.setValue(self.project.work_fund)

        if self.project.constraint_type == "duration":
            self.constraint_type_combo.setCurrentIndex(0)
            self.constraint_unit_label.setText("месяцев")
        else:
            self.constraint_type_combo.setCurrentIndex(1)
            self.constraint_unit_label.setText("человек")

        self.constraint_value_spin.setValue(self.project.constraint_value)
        self._updating = False

    def set_project(self, project: Project):
        """Установить новый проект"""
        self.project = project
        self._load_data()

    def _on_name_changed(self, text: str):
        """Обработка изменения названия"""
        if not self._updating:
            self.project.name = text
            self.data_changed.emit()

    def _on_description_changed(self):
        """Обработка изменения описания"""
        if not self._updating:
            self.project.description = self.description_edit.toPlainText()
            self.data_changed.emit()

    def _on_work_fund_changed(self, value: int):
        """Обработка изменения фонда рабочего времени"""
        if not self._updating:
            self.project.work_fund = value
            self.data_changed.emit()

    def _on_constraint_type_changed(self, index: int):
        """Обработка изменения типа ограничения"""
        if not self._updating:
            if index == 0:
                self.project.constraint_type = "duration"
                self.constraint_unit_label.setText("месяцев")
            else:
                self.project.constraint_type = "staff"
                self.constraint_unit_label.setText("человек")
            self.data_changed.emit()

    def _on_constraint_value_changed(self, value: float):
        """Обработка изменения значения ограничения"""
        if not self._updating:
            self.project.constraint_value = value
            self.data_changed.emit()
