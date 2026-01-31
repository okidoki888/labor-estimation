# -*- coding: utf-8 -*-
"""
Редактор компонентов и функций (Вкладка 2)
"""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QGroupBox, QFormLayout,
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, Signal

from ..models.project import Project, Component, FunctionInstance
from ..models.function_catalog import get_function_by_id, FunctionInfo, OperationType
from ..models.coefficients import (
    TRANSLATION_COEFFICIENTS, DEVELOPER_EXPERIENCE,
    COMPLEXITY_LEVELS, get_complexity_description
)
from .function_selector import FunctionSelectorDialog


class ComponentsEditorWidget(QWidget):
    """Редактор компонентов и функций"""

    data_changed = Signal()

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self._updating = False
        self._current_component: Optional[Component] = None
        self._current_function: Optional[FunctionInstance] = None

        self._setup_ui()
        self._refresh_tree()

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QHBoxLayout(self)

        # Разделитель для левой и правой части
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Левая часть: дерево компонентов
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Дерево
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Компонент / Функция", "Объём"])
        self.tree.setColumnWidth(0, 300)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.tree)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.btn_add_component = QPushButton("+ Компонент")
        self.btn_add_component.clicked.connect(self._add_component)
        buttons_layout.addWidget(self.btn_add_component)

        self.btn_add_function = QPushButton("+ Функция")
        self.btn_add_function.clicked.connect(self._add_function)
        buttons_layout.addWidget(self.btn_add_function)

        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.clicked.connect(self._delete_selected)
        buttons_layout.addWidget(self.btn_delete)

        self.btn_copy = QPushButton("Копировать")
        self.btn_copy.clicked.connect(self._copy_selected)
        buttons_layout.addWidget(self.btn_copy)

        left_layout.addLayout(buttons_layout)
        splitter.addWidget(left_widget)

        # Правая часть: редактирование
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Редактор компонента
        self.component_group = QGroupBox("Компонент")
        comp_layout = QFormLayout(self.component_group)

        self.comp_name_edit = QLineEdit()
        self.comp_name_edit.textChanged.connect(self._on_component_name_changed)
        comp_layout.addRow("Название:", self.comp_name_edit)

        self.comp_desc_edit = QTextEdit()
        self.comp_desc_edit.setMaximumHeight(60)
        self.comp_desc_edit.textChanged.connect(self._on_component_desc_changed)
        comp_layout.addRow("Описание:", self.comp_desc_edit)

        right_layout.addWidget(self.component_group)

        # Редактор функции
        self.function_group = QGroupBox("Функция")
        func_layout = QFormLayout(self.function_group)

        # Номер и название (не редактируются)
        self.func_id_label = QLabel("-")
        func_layout.addRow("Номер:", self.func_id_label)

        self.func_name_label = QLabel("-")
        self.func_name_label.setWordWrap(True)
        func_layout.addRow("Наименование:", self.func_name_label)

        # Пользовательское описание
        self.func_desc_edit = QTextEdit()
        self.func_desc_edit.setMaximumHeight(50)
        self.func_desc_edit.setPlaceholderText("Описание реализации в вашем проекте")
        self.func_desc_edit.textChanged.connect(self._on_function_desc_changed)
        func_layout.addRow("Описание:", self.func_desc_edit)

        # Объём
        volume_layout = QHBoxLayout()
        self.func_volume_spin = QSpinBox()
        self.func_volume_spin.setRange(1, 100000)
        self.func_volume_spin.valueChanged.connect(self._on_function_volume_changed)
        volume_layout.addWidget(self.func_volume_spin)

        self.func_volume_hint = QLabel("(диапазон: -)")
        self.func_volume_hint.setStyleSheet("color: gray;")
        volume_layout.addWidget(self.func_volume_hint)
        volume_layout.addStretch()

        func_layout.addRow("Объём Vi (строк):", volume_layout)

        # Средство разработки
        self.func_language_combo = QComboBox()
        self.func_language_combo.addItems(sorted(TRANSLATION_COEFFICIENTS.keys()))
        self.func_language_combo.currentTextChanged.connect(self._on_function_language_changed)
        func_layout.addRow("Средство разработки:", self.func_language_combo)

        # Коэффициенты языка
        self.func_kp_label = QLabel("kp = 1.00")
        self.func_ksr_label = QLabel("K_sr_razr = 1.00")
        coef_layout = QHBoxLayout()
        coef_layout.addWidget(self.func_kp_label)
        coef_layout.addWidget(self.func_ksr_label)
        coef_layout.addStretch()
        func_layout.addRow("Коэффициенты:", coef_layout)

        # Число реализаций
        self.func_reuse_count_spin = QSpinBox()
        self.func_reuse_count_spin.setRange(1, 1000)
        self.func_reuse_count_spin.setToolTip("Количество реализаций данной функции")
        self.func_reuse_count_spin.valueChanged.connect(self._on_function_reuse_count_changed)
        func_layout.addRow("Число реализаций ri:", self.func_reuse_count_spin)

        # Коэффициент повторного использования
        self.func_reuse_coef_spin = QDoubleSpinBox()
        self.func_reuse_coef_spin.setRange(0.0, 1.0)
        self.func_reuse_coef_spin.setSingleStep(0.1)
        self.func_reuse_coef_spin.setDecimals(2)
        self.func_reuse_coef_spin.setToolTip(
            "1.0 = полностью новый код\n"
            "0.0 = полностью заимствованный код"
        )
        self.func_reuse_coef_spin.valueChanged.connect(self._on_function_reuse_coef_changed)
        func_layout.addRow("Коэфф. повторного использования ki:", self.func_reuse_coef_spin)

        # Уровень сложности
        self.func_complexity_combo = QComboBox()
        for level, name in COMPLEXITY_LEVELS.items():
            self.func_complexity_combo.addItem(f"{level} — {name}", level)
        self.func_complexity_combo.currentIndexChanged.connect(self._on_function_complexity_changed)
        func_layout.addRow("Уровень сложности:", self.func_complexity_combo)

        self.func_complexity_hint = QLabel("")
        self.func_complexity_hint.setWordWrap(True)
        self.func_complexity_hint.setStyleSheet("color: gray; font-size: 10px;")
        func_layout.addRow("", self.func_complexity_hint)

        # Опыт программистов
        self.func_experience_combo = QComboBox()
        self.func_experience_combo.addItems(list(DEVELOPER_EXPERIENCE.keys()))
        self.func_experience_combo.currentTextChanged.connect(self._on_function_experience_changed)
        func_layout.addRow("Опыт программистов:", self.func_experience_combo)

        right_layout.addWidget(self.function_group)

        # Сводная таблица
        summary_group = QGroupBox("Сводка по функциям")
        summary_layout = QVBoxLayout(summary_group)

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(6)
        self.summary_table.setHorizontalHeaderLabels([
            "Функция", "Vi", "ri", "ki", "Vm", "Vk"
        ])
        self.summary_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        summary_layout.addWidget(self.summary_table)

        right_layout.addWidget(summary_group)

        splitter.addWidget(right_widget)
        splitter.setSizes([350, 550])

        # Начальное состояние
        self.component_group.setEnabled(False)
        self.function_group.setEnabled(False)

    def set_project(self, project: Project):
        """Установить новый проект"""
        self.project = project
        self._current_component = None
        self._current_function = None
        self._refresh_tree()
        self.component_group.setEnabled(False)
        self.function_group.setEnabled(False)

    def _refresh_tree(self):
        """Обновление дерева компонентов"""
        # Запоминаем текущий выбор до очистки
        current_comp_id = self._current_component.id if self._current_component else None
        current_func_id = self._current_function.id if self._current_function else None

        self.tree.clear()

        for component in self.project.components:
            comp_item = QTreeWidgetItem([component.name, ""])
            comp_item.setData(0, Qt.UserRole, ("component", component.id))
            self.tree.addTopLevelItem(comp_item)

            for func in component.functions:
                func_item = QTreeWidgetItem([
                    f"{func.function_id} {func.function_name[:40]}",
                    str(func.volume * func.reuse_count)
                ])
                func_item.setData(0, Qt.UserRole, ("function", component.id, func.id))
                comp_item.addChild(func_item)

            comp_item.setExpanded(True)

        self._refresh_summary()
        self._restore_selection(current_comp_id, current_func_id)

    def _restore_selection(self, component_id: Optional[str], function_id: Optional[str]):
        """Восстановить выбор в дереве после обновления (чтобы панели редактирования не отключались)"""
        if not component_id:
            return
        for i in range(self.tree.topLevelItemCount()):
            comp_item = self.tree.topLevelItem(i)
            data = comp_item.data(0, Qt.UserRole)
            if not data or data[1] != component_id:
                continue
            if function_id:
                for j in range(comp_item.childCount()):
                    func_item = comp_item.child(j)
                    fdata = func_item.data(0, Qt.UserRole)
                    if fdata and fdata[2] == function_id:
                        self.tree.setCurrentItem(func_item)
                        return
            self.tree.setCurrentItem(comp_item)
            return

    def _refresh_summary(self):
        """Обновление сводной таблицы"""
        functions = self.project.get_all_functions()
        self.summary_table.setRowCount(len(functions))

        from ..models.coefficients import (
            COMPLEXITY_COEFFICIENTS, DEV_ENVIRONMENT_COEFFICIENTS, DEVELOPER_EXPERIENCE
        )

        for row, func in enumerate(functions):
            # Название
            self.summary_table.setItem(row, 0, QTableWidgetItem(
                f"{func.function_id} {func.function_name[:30]}"
            ))

            # Vi
            self.summary_table.setItem(row, 1, QTableWidgetItem(str(func.volume)))

            # ri
            self.summary_table.setItem(row, 2, QTableWidgetItem(str(func.reuse_count)))

            # ki
            self.summary_table.setItem(row, 3, QTableWidgetItem(f"{func.reuse_coefficient:.2f}"))

            # Vm = Vi * ri * ki
            vm = func.volume * func.reuse_count * func.reuse_coefficient
            self.summary_table.setItem(row, 4, QTableWidgetItem(f"{vm:.0f}"))

            # Vk = Vm * K_slozhn * K_sr_razr * K_opyt
            k_slozhn = COMPLEXITY_COEFFICIENTS.get(func.complexity_level, 1.00)
            k_sr_razr = DEV_ENVIRONMENT_COEFFICIENTS.get(func.language, 1.00)
            k_opyt = DEVELOPER_EXPERIENCE.get(func.developer_experience, 1.00)
            vk = vm * k_slozhn * k_sr_razr * k_opyt
            self.summary_table.setItem(row, 5, QTableWidgetItem(f"{vk:.0f}"))

    def _on_selection_changed(self):
        """Обработка изменения выбора в дереве"""
        items = self.tree.selectedItems()
        if not items:
            self.component_group.setEnabled(False)
            self.function_group.setEnabled(False)
            return

        data = items[0].data(0, Qt.UserRole)
        if not data:
            return

        if data[0] == "component":
            self._select_component(data[1])
        elif data[0] == "function":
            self._select_function(data[1], data[2])

    def _select_component(self, component_id: str):
        """Выбор компонента"""
        self._current_component = self.project.get_component(component_id)
        self._current_function = None

        if self._current_component:
            self._updating = True
            self.comp_name_edit.setText(self._current_component.name)
            self.comp_desc_edit.setPlainText(self._current_component.description)
            self._updating = False

            self.component_group.setEnabled(True)
            self.function_group.setEnabled(False)

    def _select_function(self, component_id: str, function_id: str):
        """Выбор функции"""
        self._current_component = self.project.get_component(component_id)
        if not self._current_component:
            return

        for func in self._current_component.functions:
            if func.id == function_id:
                self._current_function = func
                break

        if self._current_function:
            self._updating = True

            # Заполняем поля
            self.func_id_label.setText(self._current_function.function_id)
            self.func_name_label.setText(self._current_function.function_name)
            self.func_desc_edit.setPlainText(self._current_function.description)
            self.func_volume_spin.setValue(self._current_function.volume)

            # Обновляем подсказку по объёму
            cat_func = get_function_by_id(self._current_function.function_id)
            if cat_func:
                self.func_volume_hint.setText(f"(диапазон: {cat_func.volume_range})")
            else:
                self.func_volume_hint.setText("(диапазон: -)")

            # Язык
            idx = self.func_language_combo.findText(self._current_function.language)
            if idx >= 0:
                self.func_language_combo.setCurrentIndex(idx)
            self._update_language_coefficients()

            self.func_reuse_count_spin.setValue(self._current_function.reuse_count)
            self.func_reuse_coef_spin.setValue(self._current_function.reuse_coefficient)

            # Сложность
            for i in range(self.func_complexity_combo.count()):
                if self.func_complexity_combo.itemData(i) == self._current_function.complexity_level:
                    self.func_complexity_combo.setCurrentIndex(i)
                    break
            self._update_complexity_hint()

            # Опыт
            idx = self.func_experience_combo.findText(self._current_function.developer_experience)
            if idx >= 0:
                self.func_experience_combo.setCurrentIndex(idx)

            self._updating = False

            self.component_group.setEnabled(True)
            self.function_group.setEnabled(True)

    def _update_language_coefficients(self):
        """Обновление отображения коэффициентов языка"""
        from ..models.coefficients import TRANSLATION_COEFFICIENTS, DEV_ENVIRONMENT_COEFFICIENTS

        lang = self.func_language_combo.currentText()
        kp = TRANSLATION_COEFFICIENTS.get(lang, 1.00)
        ksr = DEV_ENVIRONMENT_COEFFICIENTS.get(lang, 1.00)

        self.func_kp_label.setText(f"kp = {kp:.2f}")
        self.func_ksr_label.setText(f"K_sr_razr = {ksr:.2f}")

    def _update_complexity_hint(self):
        """Обновление подсказки по сложности"""
        if self._current_function:
            cat_func = get_function_by_id(self._current_function.function_id)
            if cat_func:
                op_type = cat_func.operation_type.name
                level = self.func_complexity_combo.currentData()
                hint = get_complexity_description(op_type, level)
                self.func_complexity_hint.setText(hint)
                return

        self.func_complexity_hint.setText("")

    def _add_component(self):
        """Добавление нового компонента"""
        component = self.project.add_component()
        self._refresh_tree()
        self.data_changed.emit()

        # Выбираем новый компонент
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            data = item.data(0, Qt.UserRole)
            if data and data[1] == component.id:
                self.tree.setCurrentItem(item)
                break

    def _add_function(self):
        """Добавление функции из каталога"""
        # Если нет компонента — создаём или выбираем существующий
        if not self._current_component:
            if not self.project.components:
                component = self.project.add_component()
                self._refresh_tree()
                self.data_changed.emit()
                self._current_component = component
                # Выбираем новый компонент в дереве
                for i in range(self.tree.topLevelItemCount()):
                    item = self.tree.topLevelItem(i)
                    data = item.data(0, Qt.UserRole)
                    if data and data[1] == component.id:
                        self.tree.setCurrentItem(item)
                        self.component_group.setEnabled(True)
                        self.function_group.setEnabled(False)
                        break
            else:
                # Выбираем первый компонент
                self._current_component = self.project.components[0]
                self._refresh_tree()
                for i in range(self.tree.topLevelItemCount()):
                    item = self.tree.topLevelItem(i)
                    data = item.data(0, Qt.UserRole)
                    if data and data[1] == self._current_component.id:
                        self.tree.setCurrentItem(item)
                        self.component_group.setEnabled(True)
                        self.function_group.setEnabled(False)
                        break

        if not self._current_component:
            return

        dialog = FunctionSelectorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.get_selected_functions():
            added = []
            for func_info in dialog.get_selected_functions():
                func_instance = FunctionInstance(
                    function_id=func_info.id,
                    function_name=func_info.name,
                    volume=func_info.default_volume,
                    language="C++",
                    reuse_count=1,
                    reuse_coefficient=1.0,
                    complexity_level=3,
                    developer_experience="Средний (3-4 ПС)",
                )
                self._current_component.add_function(func_instance)
                added.append(func_instance)

            self._refresh_tree()
            self.data_changed.emit()

            # Выбираем последнюю добавленную функцию
            if added:
                last = added[-1]
                for i in range(self.tree.topLevelItemCount()):
                    comp_item = self.tree.topLevelItem(i)
                    data = comp_item.data(0, Qt.UserRole)
                    if data and data[1] == self._current_component.id:
                        for j in range(comp_item.childCount()):
                            func_item = comp_item.child(j)
                            fdata = func_item.data(0, Qt.UserRole)
                            if fdata and fdata[2] == last.id:
                                self.tree.setCurrentItem(func_item)
                                break
                        break

    def _delete_selected(self):
        """Удаление выбранного элемента"""
        items = self.tree.selectedItems()
        if not items:
            return

        data = items[0].data(0, Qt.UserRole)
        if not data:
            return

        if data[0] == "component":
            reply = QMessageBox.question(
                self, "Подтверждение",
                "Удалить компонент со всеми функциями?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.project.remove_component(data[1])
                self._current_component = None
                self._refresh_tree()
                self.data_changed.emit()

        elif data[0] == "function":
            component = self.project.get_component(data[1])
            if component:
                component.remove_function(data[2])
                self._current_function = None
                self._refresh_tree()
                self.data_changed.emit()

    def _copy_selected(self):
        """Копирование выбранного элемента"""
        items = self.tree.selectedItems()
        if not items:
            return

        data = items[0].data(0, Qt.UserRole)
        if not data:
            return

        if data[0] == "component":
            original = self.project.get_component(data[1])
            if original:
                new_comp = Component(
                    name=f"{original.name} (копия)",
                    description=original.description
                )
                for func in original.functions:
                    new_func = FunctionInstance(
                        function_id=func.function_id,
                        function_name=func.function_name,
                        description=func.description,
                        volume=func.volume,
                        language=func.language,
                        reuse_count=func.reuse_count,
                        reuse_coefficient=func.reuse_coefficient,
                        complexity_level=func.complexity_level,
                        developer_experience=func.developer_experience,
                    )
                    new_comp.add_function(new_func)
                self.project.add_component(new_comp)
                self._refresh_tree()
                self.data_changed.emit()

        elif data[0] == "function":
            component = self.project.get_component(data[1])
            if component:
                for func in component.functions:
                    if func.id == data[2]:
                        new_func = FunctionInstance(
                            function_id=func.function_id,
                            function_name=func.function_name,
                            description=f"{func.description} (копия)",
                            volume=func.volume,
                            language=func.language,
                            reuse_count=func.reuse_count,
                            reuse_coefficient=func.reuse_coefficient,
                            complexity_level=func.complexity_level,
                            developer_experience=func.developer_experience,
                        )
                        component.add_function(new_func)
                        self._refresh_tree()
                        self.data_changed.emit()
                        break

    # Обработчики изменений компонента
    def _on_component_name_changed(self, text: str):
        if not self._updating and self._current_component:
            self._current_component.name = text
            self._refresh_tree()
            self.data_changed.emit()

    def _on_component_desc_changed(self):
        if not self._updating and self._current_component:
            self._current_component.description = self.comp_desc_edit.toPlainText()
            self.data_changed.emit()

    # Обработчики изменений функции
    def _on_function_desc_changed(self):
        if not self._updating and self._current_function:
            self._current_function.description = self.func_desc_edit.toPlainText()
            self.data_changed.emit()

    def _on_function_volume_changed(self, value: int):
        if not self._updating and self._current_function:
            self._current_function.volume = value

            # Проверка диапазона
            cat_func = get_function_by_id(self._current_function.function_id)
            if cat_func:
                if value < cat_func.volume_min or value > cat_func.volume_max:
                    self.func_volume_spin.setStyleSheet("background-color: #ffcccc;")
                else:
                    self.func_volume_spin.setStyleSheet("")

            self._refresh_tree()
            self._refresh_summary()
            self.data_changed.emit()

    def _on_function_language_changed(self, text: str):
        if not self._updating and self._current_function:
            self._current_function.language = text
            self._update_language_coefficients()
            self._refresh_summary()
            self.data_changed.emit()

    def _on_function_reuse_count_changed(self, value: int):
        if not self._updating and self._current_function:
            self._current_function.reuse_count = value
            self._refresh_tree()
            self._refresh_summary()
            self.data_changed.emit()

    def _on_function_reuse_coef_changed(self, value: float):
        if not self._updating and self._current_function:
            self._current_function.reuse_coefficient = value
            self._refresh_summary()
            self.data_changed.emit()

    def _on_function_complexity_changed(self, index: int):
        if not self._updating and self._current_function:
            self._current_function.complexity_level = self.func_complexity_combo.currentData()
            self._update_complexity_hint()
            self._refresh_summary()
            self.data_changed.emit()

    def _on_function_experience_changed(self, text: str):
        if not self._updating and self._current_function:
            self._current_function.developer_experience = text
            self._refresh_summary()
            self.data_changed.emit()
