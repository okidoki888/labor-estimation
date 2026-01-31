# -*- coding: utf-8 -*-
"""
Диалог выбора функции из каталога
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QComboBox, QDialogButtonBox, QLabel, QGroupBox,
    QFormLayout, QPushButton, QAbstractItemView
)
from PySide6.QtCore import Qt

from typing import Optional, List

from ..models.function_catalog import (
    FUNCTION_CATALOG, FunctionInfo, OperationType,
    get_functions_by_operation_type, search_functions
)


class FunctionSelectorDialog(QDialog):
    """Диалог выбора функций из каталога (поддержка мультивыбора и групп)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_functions: List[FunctionInfo] = []
        self._block_item_changed = False
        self._setup_ui()
        self._populate_tree()
        self._select_first_function()

    def _setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("Выбор функций из каталога")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Панель поиска и фильтрации
        filter_layout = QHBoxLayout()

        # Поиск
        filter_layout.addWidget(QLabel("Поиск:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите название функции...")
        self.search_edit.textChanged.connect(self._on_search)
        filter_layout.addWidget(self.search_edit)

        # Фильтр по типу операции
        filter_layout.addWidget(QLabel("Тип операции:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("Все типы", None)
        for op_type in OperationType:
            self.type_combo.addItem(op_type.value, op_type)
        self.type_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.type_combo)

        layout.addLayout(filter_layout)

        # Дерево функций: чекбоксы для мультивыбора (работает на всех ОС)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["✓", "Функция", "Объём", "Тип"])
        self.tree.setColumnWidth(0, 28)
        self.tree.setColumnWidth(1, 470)
        self.tree.setColumnWidth(2, 100)
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.tree)

        # Информация о выбранных функциях
        self.info_group = QGroupBox("Информация о выбранных")
        info_layout = QFormLayout(self.info_group)

        self.info_id = QLabel("-")
        info_layout.addRow("Номер:", self.info_id)

        self.info_name = QLabel("-")
        self.info_name.setWordWrap(True)
        info_layout.addRow("Наименование:", self.info_name)

        self.info_volume = QLabel("-")
        info_layout.addRow("Диапазон объёма:", self.info_volume)

        self.info_type = QLabel("-")
        info_layout.addRow("Тип операции:", self.info_type)

        self.info_func_type = QLabel("-")
        info_layout.addRow("Тип функции:", self.info_func_type)

        layout.addWidget(self.info_group)

        # Кнопки группового выбора по чекбоксам
        btn_layout = QHBoxLayout()
        self.btn_check_all = QPushButton("Отметить все видимые")
        self.btn_check_all.clicked.connect(self._check_all_visible)
        self.btn_uncheck_all = QPushButton("Снять все отметки")
        self.btn_uncheck_all.clicked.connect(self._uncheck_all)
        self.btn_add_all_visible = QPushButton("Добавить все отображаемые")
        self.btn_add_all_visible.setToolTip("Добавить в компонент все функции, показанные при текущем поиске/фильтре")
        self.btn_add_all_visible.clicked.connect(self._add_all_visible)
        btn_layout.addWidget(self.btn_check_all)
        btn_layout.addWidget(self.btn_uncheck_all)
        btn_layout.addWidget(self.btn_add_all_visible)
        layout.addLayout(btn_layout)

        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
        self.ok_button.setText("Добавить выбранные")
        layout.addWidget(button_box)

    def _populate_tree(self, functions: list[FunctionInfo] = None):
        """Заполнение дерева функций"""
        self.tree.clear()

        if functions is None:
            functions = FUNCTION_CATALOG

        # Группируем по типу операции
        by_operation = {}
        for func in functions:
            op_name = func.operation_type.value
            if op_name not in by_operation:
                by_operation[op_name] = {}
            category = func.category or "Прочее"
            if category not in by_operation[op_name]:
                by_operation[op_name][category] = []
            by_operation[op_name][category].append(func)

        # Создаём иерархию (4 колонки: чекбокс, название, объём, тип)
        self._block_item_changed = True
        try:
            for op_name, categories in sorted(by_operation.items()):
                op_item = QTreeWidgetItem(["", op_name, "", ""])
                op_item.setFlags(op_item.flags() & ~Qt.ItemIsSelectable)
                self.tree.addTopLevelItem(op_item)

                for category, funcs in sorted(categories.items()):
                    cat_item = QTreeWidgetItem(["", category, "", ""])
                    cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsSelectable)
                    op_item.addChild(cat_item)

                    for func in funcs:
                        func_item = QTreeWidgetItem([
                            "",
                            f"{func.id} {func.name}{func.type_marker}",
                            func.volume_range,
                            func.operation_type.value[:10]
                        ])
                        func_item.setData(1, Qt.UserRole, func)
                        func_item.setFlags(
                            func_item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
                        )
                        func_item.setCheckState(0, Qt.Unchecked)
                        cat_item.addChild(func_item)

                op_item.setExpanded(True)
        finally:
            self._block_item_changed = False

    def get_selected_functions(self) -> List[FunctionInfo]:
        """Вернуть список выбранных функций: отмеченные чекбоксами или выделение."""
        checked = self._get_checked_functions()
        if checked:
            return checked
        return list(self.selected_functions)

    def _get_checked_functions(self) -> List[FunctionInfo]:
        """Собрать все функции с отмеченным чекбоксом."""
        result = []

        def collect(item: QTreeWidgetItem):
            if item.checkState(0) == Qt.CheckState.Checked:
                data = item.data(1, Qt.UserRole)
                if data is not None and hasattr(data, 'id'):
                    result.append(data)
            for i in range(item.childCount()):
                collect(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            collect(self.tree.topLevelItem(i))
        return result

    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Обновить счётчик при изменении чекбокса."""
        if getattr(self, '_block_item_changed', False) or column != 0:
            return
        funcs = self._get_checked_functions()
        if funcs:
            self._update_info(funcs)
            self.ok_button.setEnabled(True)
        else:
            items = self.tree.selectedItems()
            self.selected_functions = []
            for it in items:
                data = it.data(1, Qt.UserRole)
                if data is not None and hasattr(data, 'id'):
                    self.selected_functions.append(data)
            if self.selected_functions:
                self._update_info(self.selected_functions)
                self.ok_button.setEnabled(True)
            else:
                self._clear_info()
                self.ok_button.setEnabled(False)

    def _check_all_visible(self):
        """Отметить чекбоксы у всех видимых функций."""
        self._block_item_changed = True
        try:
            for i in range(self.tree.topLevelItemCount()):
                self._set_children_check_state(self.tree.topLevelItem(i), Qt.CheckState.Checked)
        finally:
            self._block_item_changed = False
        funcs = self._get_checked_functions()
        if funcs:
            self._update_info(funcs)
            self.ok_button.setEnabled(True)

    def _uncheck_all(self):
        """Снять все отметки с чекбоксов."""
        self._block_item_changed = True
        try:
            for i in range(self.tree.topLevelItemCount()):
                self._set_children_check_state(self.tree.topLevelItem(i), Qt.CheckState.Unchecked)
        finally:
            self._block_item_changed = False
        self._clear_info()
        self.ok_button.setEnabled(False)

    def _set_children_check_state(self, item: QTreeWidgetItem, state: Qt.CheckState):
        """Рекурсивно установить состояние чекбокса для элементов с функциями."""
        data = item.data(1, Qt.UserRole)
        if data is not None and hasattr(data, 'id'):
            item.setCheckState(0, state)
        for i in range(item.childCount()):
            self._set_children_check_state(item.child(i), state)

    def _add_all_visible(self):
        """Добавить все отображаемые в дереве функции (группа по текущему фильтру)."""
        all_visible = self._collect_all_functions_in_tree()
        if all_visible:
            self.selected_functions = all_visible
            self.accept()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Каталог", "В текущем виде каталога нет функций для добавления.")

    def _collect_all_functions_in_tree(self) -> List[FunctionInfo]:
        """Собрать все функции из текущего дерева (после фильтра/поиска)."""
        result = []

        def collect(item: QTreeWidgetItem):
            data = item.data(1, Qt.UserRole)
            if data is not None and hasattr(data, 'id'):
                result.append(data)
            for i in range(item.childCount()):
                collect(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            collect(self.tree.topLevelItem(i))
        return result

    def _select_first_function(self):
        """Выбрать первую функцию в дереве для удобства"""
        def find_first_func_item(item: QTreeWidgetItem) -> Optional[QTreeWidgetItem]:
            data = item.data(1, Qt.UserRole)
            if data is not None and hasattr(data, 'id'):
                return item
            for i in range(item.childCount()):
                found = find_first_func_item(item.child(i))
                if found:
                    return found
            return None

        for i in range(self.tree.topLevelItemCount()):
            found = find_first_func_item(self.tree.topLevelItem(i))
            if found:
                self.tree.setCurrentItem(found)
                self.tree.scrollToItem(found)
                break

    def _on_search(self, text: str):
        """Обработка поиска"""
        if text:
            functions = search_functions(text)
        else:
            op_type = self.type_combo.currentData()
            if op_type:
                functions = get_functions_by_operation_type(op_type)
            else:
                functions = FUNCTION_CATALOG
        self._populate_tree(functions)
        self._select_first_function()

    def _on_filter_changed(self, index: int):
        """Обработка изменения фильтра"""
        op_type = self.type_combo.currentData()
        search_text = self.search_edit.text()

        if search_text:
            functions = search_functions(search_text)
            if op_type:
                functions = [f for f in functions if f.operation_type == op_type]
        elif op_type:
            functions = get_functions_by_operation_type(op_type)
        else:
            functions = FUNCTION_CATALOG

        self._populate_tree(functions)
        self._select_first_function()

    def _on_selection_changed(self):
        """Обработка изменения выделения (если нет отмеченных чекбоксами — показываем выделенные)"""
        if getattr(self, '_block_item_changed', False):
            return
        checked = self._get_checked_functions()
        if checked:
            return
        items = self.tree.selectedItems()
        self.selected_functions = []
        for item in items:
            data = item.data(1, Qt.UserRole)
            if data is not None and hasattr(data, 'id'):
                self.selected_functions.append(data)

        if self.selected_functions:
            self._update_info(self.selected_functions)
            self.ok_button.setEnabled(True)
        else:
            self._clear_info()
            self.ok_button.setEnabled(False)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Двойной клик — добавить эту функцию или все отмеченные чекбоксами"""
        func = item.data(1, Qt.UserRole)
        if func:
            checked = self._get_checked_functions()
            if checked:
                self.selected_functions = checked
            else:
                self.selected_functions = [func]
            self.accept()

    def _update_info(self, functions: List[FunctionInfo]):
        """Обновление информации о выбранных функциях"""
        n = len(functions)
        if n == 0:
            self._clear_info()
            return
        if n == 1:
            func = functions[0]
            self.info_id.setText(func.id)
            self.info_name.setText(func.name)
            self.info_volume.setText(f"{func.volume_range} строк на условном языке")
            self.info_type.setText(func.operation_type.value)
            type_names = {
                "atomic": "Атомарная (*)",
                "composite": "Составная (**)",
                "structural": "Структурная"
            }
            self.info_func_type.setText(type_names.get(func.function_type.value, "-"))
        else:
            self.info_id.setText(f"Выбрано: {n}")
            self.info_name.setText(", ".join(f.id for f in functions[:5]) + (" …" if n > 5 else ""))
            self.info_volume.setText(f"Всего функций: {n}")
            self.info_type.setText("")
            self.info_func_type.setText("Отметьте чекбоксы для добавления нескольких")

    def _clear_info(self):
        """Очистка информации"""
        self.info_id.setText("-")
        self.info_name.setText("-")
        self.info_volume.setText("-")
        self.info_type.setText("-")
        self.info_func_type.setText("-")
