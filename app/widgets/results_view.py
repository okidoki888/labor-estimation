# -*- coding: utf-8 -*-
"""
Виджет отображения результатов расчёта (Вкладка 4)
"""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QFrame, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from ..models.calculation import CalculationResult
from ..models.project import Project
from .chart_widget import ChartWidget


class ResultsViewWidget(QWidget):
    """Виджет отображения результатов расчёта"""

    calculate_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result: Optional[CalculationResult] = None
        self.project: Optional[Project] = None
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Кнопка расчёта (основное действие — акцент по палитре)
        self.calc_button = QPushButton("Рассчитать")
        self.calc_button.setObjectName("primaryButton")
        self.calc_button.setMinimumHeight(48)
        self.calc_button.clicked.connect(self.calculate_requested.emit)
        layout.addWidget(self.calc_button)

        # Прокручиваемая область с результатами
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Группа: Объём ПС
        self.volume_group = QGroupBox("1. Объём программного средства")
        volume_layout = QFormLayout(self.volume_group)

        self.total_volume_label = QLabel("-")
        self.total_volume_label.setStyleSheet("font-weight: 600; font-size: 1.08em;")
        volume_layout.addRow("Общий объём V:", self.total_volume_label)

        scroll_layout.addWidget(self.volume_group)

        # Группа: Базовая трудоёмкость (контраст по глобальной палитре)
        self.base_group = QGroupBox("2. Базовая трудоёмкость")
        self.base_group.setObjectName("base_group")
        base_layout = QVBoxLayout(self.base_group)

        # Формула (стили из темы — QLabel#formulaLabel)
        self.formula_label = QLabel("")
        self.formula_label.setObjectName("formulaLabel")
        self.formula_label.setWordWrap(True)
        self.formula_label.setMinimumHeight(80)
        base_layout.addWidget(self.formula_label)

        # Коэффициенты (цвет из темы — QGroupBox#base_group QLabel)
        coef_layout = QFormLayout()
        self.coef_labels = {}
        for name in ["A", "C", "V", "K_n", "K_nad", "K_proizv", "K_dokum", "K_teh", "K_or"]:
            label = QLabel("-")
            self.coef_labels[name] = label
            coef_layout.addRow(f"{name}:", label)

        base_layout.addLayout(coef_layout)

        base_caption = QLabel("Базовая трудоёмкость:")
        self.base_labor_label = QLabel("-")
        self.base_labor_label.setObjectName("baseLaborLabel")
        base_layout.addWidget(base_caption)
        base_layout.addWidget(self.base_labor_label)

        scroll_layout.addWidget(self.base_group)

        # Группа: Подпроцессы
        self.subprocess_group = QGroupBox("3. Трудоёмкость подпроцессов")
        subprocess_layout = QVBoxLayout(self.subprocess_group)

        self.subprocess_table = QTableWidget()
        self.subprocess_table.setColumnCount(6)
        self.subprocess_table.setHorizontalHeaderLabels([
            "Подпроцесс", "Коэфф. A", "Коэффициенты", "Трудоёмкость\n[чел.-дн.]", "Численность\n[чел.]", "Срок\n[мес.]"
        ])
        self.subprocess_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.subprocess_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.subprocess_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.subprocess_table.setMinimumHeight(200)
        subprocess_layout.addWidget(self.subprocess_table)

        scroll_layout.addWidget(self.subprocess_group)

        # Группа: Итоги
        self.totals_group = QGroupBox("4. Итоговые показатели")
        totals_layout = QFormLayout(self.totals_group)

        self.total_labor_label = QLabel("-")
        self.total_labor_label.setStyleSheet("font-weight: 600; font-size: 1.15em;")
        totals_layout.addRow("Трудоёмкость разработки T_razr:", self.total_labor_label)

        self.k_srok_label = QLabel("-")
        totals_layout.addRow("Коэффициент сроков K_sr_srok:", self.k_srok_label)

        self.final_labor_label = QLabel("-")
        self.final_labor_label.setObjectName("finalLaborLabel")
        self.final_labor_label.setStyleSheet("font-weight: 600; font-size: 1.15em;")
        totals_layout.addRow("Итоговая трудоёмкость T_srok:", self.final_labor_label)

        self.duration_label = QLabel("-")
        self.duration_label.setStyleSheet("font-weight: 600;")
        totals_layout.addRow("Общий срок:", self.duration_label)

        self.staff_label = QLabel("-")
        self.staff_label.setStyleSheet("font-weight: 600;")
        totals_layout.addRow("Средняя численность:", self.staff_label)

        scroll_layout.addWidget(self.totals_group)

        # Диаграммы
        self.charts_group = QGroupBox("5. Диаграммы")
        charts_layout = QHBoxLayout(self.charts_group)

        self.pie_chart = ChartWidget("pie")
        self.pie_chart.setMinimumHeight(300)
        charts_layout.addWidget(self.pie_chart)

        self.bar_chart = ChartWidget("bar")
        self.bar_chart.setMinimumHeight(300)
        charts_layout.addWidget(self.bar_chart)

        scroll_layout.addWidget(self.charts_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

    def clear(self):
        """Очистить результаты"""
        self.result = None
        self.project = None

        self.total_volume_label.setText("-")
        self.formula_label.setText("")
        for label in self.coef_labels.values():
            label.setText("-")
        self.base_labor_label.setText("-")
        self.subprocess_table.setRowCount(0)
        self.total_labor_label.setText("-")
        self.k_srok_label.setText("-")
        self.final_labor_label.setText("-")
        self.duration_label.setText("-")
        self.staff_label.setText("-")

        self.pie_chart.clear()
        self.bar_chart.clear()

    def update_results(self, result: CalculationResult, project: Project):
        """Обновить отображение результатов"""
        self.result = result
        self.project = project

        # 1. Объём
        self.total_volume_label.setText(f"{result.total_volume:.2f} строк условного кода")

        # 2. Базовая трудоёмкость (по строкам для читаемости)
        formula = (
            "T_baz = A × V^C × K_n × K_nad × K_proizv × K_dokum × K_teh × K_or\n\n"
            f"Подстановка: T_baz = {result.A} × {result.total_volume:.2f}^{result.C} × "
            f"{result.k_n} × {result.k_nad} × {result.k_proizv} × "
            f"{result.k_dokum} × {result.k_teh:.4f} × {result.k_or}\n\n"
            f"T_baz = {result.base_labor:.2f} чел.-дн."
        )
        self.formula_label.setText(formula)

        self.coef_labels["A"].setText(f"{result.A}")
        self.coef_labels["C"].setText(f"{result.C}")
        self.coef_labels["V"].setText(f"{result.total_volume:.2f} строк")
        self.coef_labels["K_n"].setText(f"{result.k_n} (степень новизны)")
        self.coef_labels["K_nad"].setText(f"{result.k_nad} (надёжность)")
        self.coef_labels["K_proizv"].setText(f"{result.k_proizv} (производительность)")
        self.coef_labels["K_dokum"].setText(f"{result.k_dokum} (документация)")
        self.coef_labels["K_teh"].setText(f"{result.k_teh:.4f} (технологии)")
        self.coef_labels["K_or"].setText(f"{result.k_or} (опыт разработки)")

        self.base_labor_label.setText(f"T_baz = {result.base_labor:.2f} чел.-дн.")

        # 3. Подпроцессы
        self.subprocess_table.setRowCount(len(result.subprocess_results) + 1)

        for row, sp in enumerate(result.subprocess_results):
            self.subprocess_table.setItem(row, 0, QTableWidgetItem(sp.name))
            self.subprocess_table.setItem(row, 1, QTableWidgetItem(f"{sp.base_coefficient}"))

            coef_str = ", ".join(f"{k}={v:.2f}" for k, v in sp.coefficients.items())
            self.subprocess_table.setItem(row, 2, QTableWidgetItem(coef_str))

            self.subprocess_table.setItem(row, 3, QTableWidgetItem(f"{sp.labor:.2f}"))
            self.subprocess_table.setItem(row, 4, QTableWidgetItem(f"{sp.staff:.2f}"))
            self.subprocess_table.setItem(row, 5, QTableWidgetItem(f"{sp.duration:.2f}"))

        # Итоговая строка
        last_row = len(result.subprocess_results)
        self.subprocess_table.setItem(last_row, 0, QTableWidgetItem("ИТОГО"))
        self.subprocess_table.setItem(last_row, 1, QTableWidgetItem("1.00"))
        self.subprocess_table.setItem(last_row, 2, QTableWidgetItem("-"))
        self.subprocess_table.setItem(last_row, 3, QTableWidgetItem(f"{result.total_labor:.2f}"))

        total_staff = sum(sp.staff for sp in result.subprocess_results) / len(result.subprocess_results) if result.subprocess_results else 0
        self.subprocess_table.setItem(last_row, 4, QTableWidgetItem(f"{result.average_staff:.2f}"))
        self.subprocess_table.setItem(last_row, 5, QTableWidgetItem(f"{result.total_duration:.2f}"))

        # Выделяем итоговую строку (нейтральный фон по палитре)
        for col in range(6):
            item = self.subprocess_table.item(last_row, col)
            if item:
                item.setBackground(QColor("#EEEEEE"))

        # 4. Итоги
        self.total_labor_label.setText(f"{result.total_labor:.2f} чел.-дн.")
        self.k_srok_label.setText(f"{result.k_sr_srok}")
        self.final_labor_label.setText(f"{result.final_labor:.2f} чел.-дн.")
        self.duration_label.setText(f"{result.total_duration:.2f} месяцев")
        self.staff_label.setText(f"{result.average_staff:.2f} человек")

        # 5. Диаграммы
        # Круговая диаграмма подпроцессов
        pie_data = {sp.name: sp.labor for sp in result.subprocess_results}
        self.pie_chart.update_pie_chart(pie_data, "Распределение трудоёмкости по подпроцессам")

        # Столбчатая диаграмма по компонентам
        if project:
            bar_data = {}
            for fr in result.functions_results:
                comp_name = fr.component_name
                if comp_name not in bar_data:
                    bar_data[comp_name] = 0
                bar_data[comp_name] += fr.volume_adjusted

            self.bar_chart.update_bar_chart(bar_data, "Объём по компонентам (Vk)")
