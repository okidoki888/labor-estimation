# -*- coding: utf-8 -*-
"""
Комплексная проверка функционала приложения
"""

import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Отключаем GUI для headless-тестирования
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

def run_tests():
    errors = []
    passed = 0

    # 1. Импорты
    print("\n[1/12] Проверка импортов...")
    try:
        from app.models.project import Project, Component, FunctionInstance
        from app.models.calculation import CalculationEngine, CalculationResult, FunctionResult
        from app.models.function_catalog import FUNCTION_CATALOG, get_function_by_id
        from app.models.coefficients import NOVELTY_COEFFICIENTS
        from app.export.docx_export import export_to_docx
        from app.export.xlsx_export import export_to_xlsx
        print("  ✓ Все модули импортированы")
        passed += 1
    except Exception as e:
        errors.append(f"Импорты: {e}")
        print(f"  ✗ {e}")
        return errors

    # 2. Модель проекта
    print("\n[2/12] Модель проекта...")
    try:
        p = Project()
        assert p.name == "Новый проект"
        assert len(p.components) == 0
        p.name = "Тест"
        p.description = "Описание"
        assert p.name == "Тест"
        print("  ✓ Создание и редактирование проекта")
        passed += 1
    except Exception as e:
        errors.append(f"Модель проекта: {e}")
        print(f"  ✗ {e}")

    # 3. Эталонный пример
    print("\n[3/12] Эталонный пример...")
    try:
        p = Project.create_example()
        assert len(p.components) == 5
        assert p.get_function_count() == 8
        total = p.get_total_volume()
        assert total > 0
        print(f"  ✓ 5 компонентов, 8 функций, объём={total}")
        passed += 1
    except Exception as e:
        errors.append(f"Эталонный пример: {e}")
        print(f"  ✗ {e}")

    # 4. Расчёт
    print("\n[4/12] Движок расчёта...")
    try:
        engine = CalculationEngine()
        result = engine.calculate(Project.create_example())
        assert result.total_volume > 0
        assert result.base_labor > 0
        assert len(result.subprocess_results) == 5
        assert abs(result.total_labor - sum(sp.labor for sp in result.subprocess_results)) < 0.1
        print(f"  ✓ V={result.total_volume}, T_baz={result.base_labor}, T_razr={result.total_labor}")
        passed += 1
    except Exception as e:
        errors.append(f"Расчёт: {e}")
        print(f"  ✗ {e}")

    # 5. Сохранение/загрузка проекта
    print("\n[5/12] Сохранение и загрузка проекта...")
    try:
        p = Project.create_example()
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        try:
            p.save(path)
            loaded = Project.load(path)
            assert loaded.name == p.name
            assert len(loaded.components) == len(p.components)
        finally:
            os.unlink(path)
        print("  ✓ Проект сохранён и загружен")
        passed += 1
    except Exception as e:
        errors.append(f"Сохранение/загрузка: {e}")
        print(f"  ✗ {e}")

    # 6. Экспорт в Word
    print("\n[6/12] Экспорт в Word...")
    try:
        p = Project.create_example()
        result = CalculationEngine().calculate(p)
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            path = f.name
        try:
            export_to_docx(p, result, path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 1000
            print(f"  ✓ Файл создан ({os.path.getsize(path)} байт)")
        finally:
            os.unlink(path)
        passed += 1
    except Exception as e:
        errors.append(f"Экспорт Word: {e}")
        print(f"  ✗ {e}")

    # 7. Экспорт в Excel
    print("\n[7/12] Экспорт в Excel...")
    try:
        p = Project.create_example()
        result = CalculationEngine().calculate(p)
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            path = f.name
        try:
            export_to_xlsx(p, result, path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 1000
            print(f"  ✓ Файл создан ({os.path.getsize(path)} байт)")
        finally:
            os.unlink(path)
        passed += 1
    except Exception as e:
        errors.append(f"Экспорт Excel: {e}")
        print(f"  ✗ {e}")

    # 8. Каталог функций
    print("\n[8/12] Каталог функций...")
    try:
        assert len(FUNCTION_CATALOG) > 0
        func = get_function_by_id("1.1.1")
        assert func is not None
        assert hasattr(func, 'volume_min')
        assert hasattr(func, 'volume_max')
        print(f"  ✓ {len(FUNCTION_CATALOG)} функций в каталоге")
        passed += 1
    except Exception as e:
        errors.append(f"Каталог: {e}")
        print(f"  ✗ {e}")

    # 9. FunctionResult атрибуты для экспорта
    print("\n[9/12] FunctionResult (экспорт Excel)...")
    try:
        result = CalculationEngine().calculate(Project.create_example())
        fr = result.functions_results[0]
        assert hasattr(fr, 'k_slozhn')
        assert hasattr(fr, 'k_sr_razr')
        assert hasattr(fr, 'k_opyt')
        assert hasattr(fr, 'function_id')
        print("  ✓ Все атрибуты FunctionResult присутствуют")
        passed += 1
    except Exception as e:
        errors.append(f"FunctionResult: {e}")
        print(f"  ✗ {e}")

    # 10. Инициализация GUI (headless)
    print("\n[10/12] Инициализация главного окна...")
    try:
        from PySide6.QtWidgets import QApplication
        from app.main_window import MainWindow
        app = QApplication.instance() or QApplication(sys.argv)
        w = MainWindow()
        assert w.tabs.count() == 5
        assert w.project is not None
        w.close()
        print("  ✓ Главное окно создано, 5 вкладок")
        passed += 1
    except Exception as e:
        errors.append(f"GUI: {e}")
        print(f"  ✗ {e}")

    # 11. Пустой проект — расчёт не выполняется
    print("\n[11/12] Валидация (пустой проект)...")
    try:
        p = Project()
        engine = CalculationEngine()
        result = engine.calculate(p)
        assert result.total_volume == 0
        assert result.base_labor == 0
        print("  ✓ Пустой проект: V=0, T_baz=0")
        passed += 1
    except Exception as e:
        errors.append(f"Валидация: {e}")
        print(f"  ✗ {e}")

    # 12. Проект с одним компонентом и функцией
    print("\n[12/12] Минимальный проект...")
    try:
        p = Project()
        p.name = "Мини-проект"
        comp = Component(name="Компонент 1")
        func_info = get_function_by_id("1.1.1")
        fi = FunctionInstance(
            function_id=func_info.id,
            function_name=func_info.name,
            volume=func_info.default_volume,
        )
        comp.functions.append(fi)
        p.add_component(comp)
        result = CalculationEngine().calculate(p)
        assert result.total_volume > 0
        assert len(result.functions_results) == 1
        print(f"  ✓ 1 компонент, 1 функция, V={result.total_volume:.0f}")
        passed += 1
    except Exception as e:
        errors.append(f"Минимальный проект: {e}")
        print(f"  ✗ {e}")

    return errors, passed


if __name__ == "__main__":
    print("=" * 60)
    print("КОМПЛЕКСНАЯ ПРОВЕРКА ФУНКЦИОНАЛА ПРИЛОЖЕНИЯ")
    print("=" * 60)

    result = run_tests()
    if isinstance(result, tuple):
        errors, passed = result
    else:
        errors = result
        passed = 0

    print("\n" + "=" * 60)
    if errors:
        print(f"РЕЗУЛЬТАТ: {passed}/12 проверок пройдено")
        print("ОШИБКИ:")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)
    else:
        print("ВСЕ 12 ПРОВЕРОК ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        sys.exit(0)
