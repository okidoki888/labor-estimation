# -*- coding: utf-8 -*-
"""
Панель выбора коэффициентов (Вкладка 3)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QGroupBox, QFormLayout, QComboBox, QListWidget,
    QListWidgetItem, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal

from ..models.project import Project
from ..models.coefficients import (
    NOVELTY_COEFFICIENTS,
    RELIABILITY_COEFFICIENTS,
    PERFORMANCE_COEFFICIENTS,
    DOCUMENTATION_COEFFICIENTS,
    DEVELOPMENT_EXPERIENCE,
    STRUCTURE_COEFFICIENTS,
    INTERACTION_TECHNOLOGIES,
    DEADLINE_COEFFICIENTS,
    ANALYST_QUALIFICATION,
    ANALYST_EXPERIENCE,
    DESIGNER_QUALIFICATION,
    DESIGNER_EXPERIENCE,
    DESIGN_TOOLS,
    PROGRAMMER_QUALIFICATION,
    IDE_COEFFICIENTS,
    TESTER_QUALIFICATION,
    TESTING_TOOLS,
    DB_SIZE,
    DEPLOYMENT_QUALIFICATION,
)


class CoefficientComboBox(QComboBox):
    """ComboBox для коэффициента с отображением значения"""

    def __init__(self, coefficients: dict, parent=None):
        super().__init__(parent)
        self.coefficients = coefficients
        self._value_label = None

        for name, value in coefficients.items():
            self.addItem(name, value)

    def set_value_label(self, label: QLabel):
        """Установить метку для отображения значения"""
        self._value_label = label
        self.currentIndexChanged.connect(self._update_value_label)
        self._update_value_label()

    def _update_value_label(self):
        """Обновить метку значения"""
        if self._value_label:
            value = self.currentData()
            if value is not None:
                self._value_label.setText(f"= {value:.2f}")


class CoefficientsPanelWidget(QWidget):
    """Панель выбора коэффициентов"""

    data_changed = Signal()

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self._updating = False
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Настройка интерфейса"""
        main_layout = QVBoxLayout(self)

        # Прокручиваемая область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)

        # === Секция 1: Уровень расчёта ===
        calc_group = QGroupBox("Коэффициенты уровня расчёта")
        calc_layout = QFormLayout(calc_group)

        # K_n — Степень новизны
        self.novelty_combo, novelty_label = self._create_coef_row(
            NOVELTY_COEFFICIENTS, "K_n"
        )
        self.novelty_combo.setToolTip(
            "K_n — степень новизны программного средства.\n"
            "Определяется по Таблице 3.1 методики."
        )
        self.novelty_combo.currentIndexChanged.connect(self._on_novelty_changed)
        calc_layout.addRow("Степень новизны (K_n):", self._wrap_with_label(self.novelty_combo, novelty_label))

        # K_nad — Требования к надёжности
        self.reliability_combo, reliability_label = self._create_coef_row(
            RELIABILITY_COEFFICIENTS, "K_nad"
        )
        self.reliability_combo.currentIndexChanged.connect(self._on_reliability_changed)
        calc_layout.addRow("Требования к надёжности (K_nad):", self._wrap_with_label(self.reliability_combo, reliability_label))

        # K_proizv — Требования к производительности
        self.performance_combo, performance_label = self._create_coef_row(
            PERFORMANCE_COEFFICIENTS, "K_proizv"
        )
        self.performance_combo.currentIndexChanged.connect(self._on_performance_changed)
        calc_layout.addRow("Требования к производительности (K_proizv):", self._wrap_with_label(self.performance_combo, performance_label))

        # K_dokum — Документация
        self.documentation_combo, documentation_label = self._create_coef_row(
            DOCUMENTATION_COEFFICIENTS, "K_dokum"
        )
        self.documentation_combo.currentIndexChanged.connect(self._on_documentation_changed)
        calc_layout.addRow("Информативность документации (K_dokum):", self._wrap_with_label(self.documentation_combo, documentation_label))

        # K_or — Опыт разработки
        self.dev_experience_combo, dev_experience_label = self._create_coef_row(
            DEVELOPMENT_EXPERIENCE, "K_or"
        )
        self.dev_experience_combo.currentIndexChanged.connect(self._on_dev_experience_changed)
        calc_layout.addRow("Опыт разработки ПС (K_or):", self._wrap_with_label(self.dev_experience_combo, dev_experience_label))

        # K_str — Структура ПС
        self.structure_combo, structure_label = self._create_coef_row(
            STRUCTURE_COEFFICIENTS, "K_str"
        )
        self.structure_combo.currentIndexChanged.connect(self._on_structure_changed)
        calc_layout.addRow("Структура ПС (K_str):", self._wrap_with_label(self.structure_combo, structure_label))

        # K_t — Технологии взаимодействия (множественный выбор)
        self.tech_list = QListWidget()
        self.tech_list.setMaximumHeight(120)
        for name, value in INTERACTION_TECHNOLOGIES.items():
            item = QListWidgetItem(f"{name} (K_t = {value:.2f})")
            item.setData(Qt.UserRole, name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.tech_list.addItem(item)
        self.tech_list.itemChanged.connect(self._on_tech_changed)
        calc_layout.addRow("Технологии взаимодействия (K_t):", self.tech_list)

        # K_sr_srok — Влияние сроков
        self.deadline_combo, deadline_label = self._create_coef_row(
            DEADLINE_COEFFICIENTS, "K_sr_srok"
        )
        self.deadline_combo.currentIndexChanged.connect(self._on_deadline_changed)
        calc_layout.addRow("Влияние сроков (K_sr_srok):", self._wrap_with_label(self.deadline_combo, deadline_label))

        layout.addWidget(calc_group)

        # === Секция 2: Подпроцессы ===
        # Анализ
        analysis_group = QGroupBox("Подпроцесс: Анализ")
        analysis_layout = QFormLayout(analysis_group)

        self.analyst_qual_combo, analyst_qual_label = self._create_coef_row(
            ANALYST_QUALIFICATION, "K_kval_an"
        )
        self.analyst_qual_combo.currentIndexChanged.connect(self._on_analyst_qual_changed)
        analysis_layout.addRow("Квалификация аналитиков:", self._wrap_with_label(self.analyst_qual_combo, analyst_qual_label))

        self.analyst_exp_combo, analyst_exp_label = self._create_coef_row(
            ANALYST_EXPERIENCE, "K_opyt_an"
        )
        self.analyst_exp_combo.currentIndexChanged.connect(self._on_analyst_exp_changed)
        analysis_layout.addRow("Опыт аналитиков:", self._wrap_with_label(self.analyst_exp_combo, analyst_exp_label))

        layout.addWidget(analysis_group)

        # Проектирование
        design_group = QGroupBox("Подпроцесс: Проектирование")
        design_layout = QFormLayout(design_group)

        self.designer_qual_combo, designer_qual_label = self._create_coef_row(
            DESIGNER_QUALIFICATION, "K_kval_pr"
        )
        self.designer_qual_combo.currentIndexChanged.connect(self._on_designer_qual_changed)
        design_layout.addRow("Квалификация проектировщиков:", self._wrap_with_label(self.designer_qual_combo, designer_qual_label))

        self.designer_exp_combo, designer_exp_label = self._create_coef_row(
            DESIGNER_EXPERIENCE, "K_opyt_pr"
        )
        self.designer_exp_combo.currentIndexChanged.connect(self._on_designer_exp_changed)
        design_layout.addRow("Опыт проектировщиков:", self._wrap_with_label(self.designer_exp_combo, designer_exp_label))

        self.design_tools_combo, design_tools_label = self._create_coef_row(
            DESIGN_TOOLS, "K_sr_pr"
        )
        self.design_tools_combo.currentIndexChanged.connect(self._on_design_tools_changed)
        design_layout.addRow("Средства проектирования:", self._wrap_with_label(self.design_tools_combo, design_tools_label))

        layout.addWidget(design_group)

        # Программирование
        prog_group = QGroupBox("Подпроцесс: Программирование")
        prog_layout = QFormLayout(prog_group)

        self.programmer_qual_combo, programmer_qual_label = self._create_coef_row(
            PROGRAMMER_QUALIFICATION, "K_kval_prog"
        )
        self.programmer_qual_combo.currentIndexChanged.connect(self._on_programmer_qual_changed)
        prog_layout.addRow("Квалификация программистов:", self._wrap_with_label(self.programmer_qual_combo, programmer_qual_label))

        self.ide_combo, ide_label = self._create_coef_row(
            IDE_COEFFICIENTS, "K_sr"
        )
        self.ide_combo.currentIndexChanged.connect(self._on_ide_changed)
        prog_layout.addRow("Среда разработки:", self._wrap_with_label(self.ide_combo, ide_label))

        layout.addWidget(prog_group)

        # Тестирование
        test_group = QGroupBox("Подпроцесс: Тестирование")
        test_layout = QFormLayout(test_group)

        self.tester_qual_combo, tester_qual_label = self._create_coef_row(
            TESTER_QUALIFICATION, "K_kval_test"
        )
        self.tester_qual_combo.currentIndexChanged.connect(self._on_tester_qual_changed)
        test_layout.addRow("Квалификация тестировщиков:", self._wrap_with_label(self.tester_qual_combo, tester_qual_label))

        self.testing_tools_combo, testing_tools_label = self._create_coef_row(
            TESTING_TOOLS, "K_sr_ts"
        )
        self.testing_tools_combo.currentIndexChanged.connect(self._on_testing_tools_changed)
        test_layout.addRow("Средства тестирования:", self._wrap_with_label(self.testing_tools_combo, testing_tools_label))

        self.db_size_combo, db_size_label = self._create_coef_row(
            DB_SIZE, "K_BD"
        )
        self.db_size_combo.currentIndexChanged.connect(self._on_db_size_changed)
        test_layout.addRow("Размер БД:", self._wrap_with_label(self.db_size_combo, db_size_label))

        layout.addWidget(test_group)

        # Ввод в действие
        deploy_group = QGroupBox("Подпроцесс: Ввод в действие")
        deploy_layout = QFormLayout(deploy_group)

        self.deploy_qual_combo, deploy_qual_label = self._create_coef_row(
            DEPLOYMENT_QUALIFICATION, "K_kval_vn"
        )
        self.deploy_qual_combo.currentIndexChanged.connect(self._on_deploy_qual_changed)
        deploy_layout.addRow("Квалификация персонала:", self._wrap_with_label(self.deploy_qual_combo, deploy_qual_label))

        layout.addWidget(deploy_group)

        layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

    def _create_coef_row(self, coefficients: dict, name: str):
        """Создать ComboBox с меткой значения"""
        combo = CoefficientComboBox(coefficients)
        label = QLabel("= 1.00")
        label.setMinimumWidth(60)
        combo.set_value_label(label)
        return combo, label

    def _wrap_with_label(self, combo: QComboBox, label: QLabel) -> QWidget:
        """Обернуть ComboBox и Label в виджет"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(combo, 1)
        layout.addWidget(label)
        return widget

    def set_project(self, project: Project):
        """Установить новый проект"""
        self.project = project
        self._load_data()

    def _load_data(self):
        """Загрузка данных из проекта"""
        self._updating = True
        coeffs = self.project.coefficients

        self._set_combo_value(self.novelty_combo, coeffs.novelty)
        self._set_combo_value(self.reliability_combo, coeffs.reliability)
        self._set_combo_value(self.performance_combo, coeffs.performance)
        self._set_combo_value(self.documentation_combo, coeffs.documentation)
        self._set_combo_value(self.dev_experience_combo, coeffs.dev_experience)
        self._set_combo_value(self.structure_combo, coeffs.structure)
        self._set_combo_value(self.deadline_combo, coeffs.deadline)

        # Технологии взаимодействия
        for i in range(self.tech_list.count()):
            item = self.tech_list.item(i)
            tech_name = item.data(Qt.UserRole)
            if tech_name in coeffs.interaction_technologies:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

        # Подпроцессы
        self._set_combo_value(self.analyst_qual_combo, coeffs.analyst_qualification)
        self._set_combo_value(self.analyst_exp_combo, coeffs.analyst_experience)
        self._set_combo_value(self.designer_qual_combo, coeffs.designer_qualification)
        self._set_combo_value(self.designer_exp_combo, coeffs.designer_experience)
        self._set_combo_value(self.design_tools_combo, coeffs.design_tools)
        self._set_combo_value(self.programmer_qual_combo, coeffs.programmer_qualification)
        self._set_combo_value(self.ide_combo, coeffs.ide)
        self._set_combo_value(self.tester_qual_combo, coeffs.tester_qualification)
        self._set_combo_value(self.testing_tools_combo, coeffs.testing_tools)
        self._set_combo_value(self.db_size_combo, coeffs.db_size)
        self._set_combo_value(self.deploy_qual_combo, coeffs.deployment_qualification)

        self._updating = False

    def _set_combo_value(self, combo: QComboBox, value: str):
        """Установить значение ComboBox по тексту"""
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    # Обработчики изменений
    def _on_novelty_changed(self):
        if not self._updating:
            self.project.coefficients.novelty = self.novelty_combo.currentText()
            self.data_changed.emit()

    def _on_reliability_changed(self):
        if not self._updating:
            self.project.coefficients.reliability = self.reliability_combo.currentText()
            self.data_changed.emit()

    def _on_performance_changed(self):
        if not self._updating:
            self.project.coefficients.performance = self.performance_combo.currentText()
            self.data_changed.emit()

    def _on_documentation_changed(self):
        if not self._updating:
            self.project.coefficients.documentation = self.documentation_combo.currentText()
            self.data_changed.emit()

    def _on_dev_experience_changed(self):
        if not self._updating:
            self.project.coefficients.dev_experience = self.dev_experience_combo.currentText()
            self.data_changed.emit()

    def _on_structure_changed(self):
        if not self._updating:
            self.project.coefficients.structure = self.structure_combo.currentText()
            self.data_changed.emit()

    def _on_tech_changed(self, item: QListWidgetItem):
        if not self._updating:
            techs = []
            for i in range(self.tech_list.count()):
                it = self.tech_list.item(i)
                if it.checkState() == Qt.Checked:
                    techs.append(it.data(Qt.UserRole))
            self.project.coefficients.interaction_technologies = techs
            self.data_changed.emit()

    def _on_deadline_changed(self):
        if not self._updating:
            self.project.coefficients.deadline = self.deadline_combo.currentText()
            self.data_changed.emit()

    def _on_analyst_qual_changed(self):
        if not self._updating:
            self.project.coefficients.analyst_qualification = self.analyst_qual_combo.currentText()
            self.data_changed.emit()

    def _on_analyst_exp_changed(self):
        if not self._updating:
            self.project.coefficients.analyst_experience = self.analyst_exp_combo.currentText()
            self.data_changed.emit()

    def _on_designer_qual_changed(self):
        if not self._updating:
            self.project.coefficients.designer_qualification = self.designer_qual_combo.currentText()
            self.data_changed.emit()

    def _on_designer_exp_changed(self):
        if not self._updating:
            self.project.coefficients.designer_experience = self.designer_exp_combo.currentText()
            self.data_changed.emit()

    def _on_design_tools_changed(self):
        if not self._updating:
            self.project.coefficients.design_tools = self.design_tools_combo.currentText()
            self.data_changed.emit()

    def _on_programmer_qual_changed(self):
        if not self._updating:
            self.project.coefficients.programmer_qualification = self.programmer_qual_combo.currentText()
            self.data_changed.emit()

    def _on_ide_changed(self):
        if not self._updating:
            self.project.coefficients.ide = self.ide_combo.currentText()
            self.data_changed.emit()

    def _on_tester_qual_changed(self):
        if not self._updating:
            self.project.coefficients.tester_qualification = self.tester_qual_combo.currentText()
            self.data_changed.emit()

    def _on_testing_tools_changed(self):
        if not self._updating:
            self.project.coefficients.testing_tools = self.testing_tools_combo.currentText()
            self.data_changed.emit()

    def _on_db_size_changed(self):
        if not self._updating:
            self.project.coefficients.db_size = self.db_size_combo.currentText()
            self.data_changed.emit()

    def _on_deploy_qual_changed(self):
        if not self._updating:
            self.project.coefficients.deployment_qualification = self.deploy_qual_combo.currentText()
            self.data_changed.emit()
