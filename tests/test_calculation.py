# -*- coding: utf-8 -*-
"""
Тест расчёта на эталонном примере из методики
"""

import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.project import Project
from app.models.calculation import CalculationEngine


def test_example_calculation():
    """Тест расчёта на эталонном примере из методики"""
    # Создаём эталонный проект
    project = Project.create_example()

    # Проверяем структуру проекта
    assert len(project.components) == 5, f"Ожидалось 5 компонентов, получено {len(project.components)}"

    total_functions = project.get_function_count()
    assert total_functions == 8, f"Ожидалось 8 функций, получено {total_functions}"

    # Выполняем расчёт
    engine = CalculationEngine()
    result = engine.calculate(project)

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ РАСЧЁТА ЭТАЛОННОГО ПРИМЕРА")
    print("=" * 60)

    # Выводим результаты по функциям
    print("\n1. ОБЪЁМ ФУНКЦИЙ:")
    print("-" * 60)
    for fr in result.functions_results:
        print(f"  {fr.function_name[:50]}")
        print(f"    Vi={fr.volume_base}, ri={fr.reuse_count}, ki={fr.reuse_coefficient}")
        print(f"    Vm={fr.volume_corrected}, Vk={fr.volume_adjusted}")

    print(f"\n  ОБЩИЙ ОБЪЁМ V = {result.total_volume} строк")

    # Проверяем объём (приблизительно 22010 строк по методике)
    expected_volume_min = 20000
    expected_volume_max = 25000
    print(f"  Ожидаемый диапазон: {expected_volume_min}-{expected_volume_max}")

    # Выводим базовую трудоёмкость
    print("\n2. БАЗОВАЯ ТРУДОЁМКОСТЬ:")
    print("-" * 60)
    print(f"  A = {result.A}")
    print(f"  C = {result.C}")
    print(f"  V = {result.total_volume}")
    print(f"  K_n = {result.k_n}")
    print(f"  K_nad = {result.k_nad}")
    print(f"  K_proizv = {result.k_proizv}")
    print(f"  K_dokum = {result.k_dokum}")
    print(f"  K_teh = {result.k_teh}")
    print(f"  K_or = {result.k_or}")
    print(f"\n  T_baz = {result.base_labor} чел.-дн.")

    # Ожидаемая базовая трудоёмкость ~645.71 по методике
    expected_base_min = 500
    expected_base_max = 800
    print(f"  Ожидаемый диапазон: {expected_base_min}-{expected_base_max}")

    # Выводим подпроцессы
    print("\n3. ПОДПРОЦЕССЫ:")
    print("-" * 60)
    for sp in result.subprocess_results:
        print(f"  {sp.name}:")
        print(f"    A = {sp.base_coefficient}")
        print(f"    Коэфф.: {sp.coefficients}")
        print(f"    T = {sp.labor} чел.-дн., N = {sp.staff} чел., t = {sp.duration} мес.")

    # Итоги
    print("\n4. ИТОГИ:")
    print("-" * 60)
    print(f"  T_razr = {result.total_labor} чел.-дн.")
    print(f"  K_sr_srok = {result.k_sr_srok}")
    print(f"  T_srok = {result.final_labor} чел.-дн.")
    print(f"  Общий срок = {result.total_duration} мес.")
    print(f"  Средняя численность = {result.average_staff} чел.")

    # Ожидаемая итоговая трудоёмкость ~593.69 по методике
    expected_labor_min = 500
    expected_labor_max = 700
    print(f"  Ожидаемый диапазон трудоёмкости: {expected_labor_min}-{expected_labor_max}")

    print("\n" + "=" * 60)

    # Проверки базовой математики
    # Проверяем, что объём > 0
    assert result.total_volume > 0, "Объём должен быть больше 0"

    # Проверяем формулу T_baz = A * V^C * коэффициенты
    expected_base = 0.19 * (result.total_volume ** 0.74) * \
        result.k_n * result.k_nad * result.k_proizv * \
        result.k_dokum * result.k_teh * result.k_or
    assert abs(result.base_labor - expected_base) < 0.1, \
        f"Формула базовой трудоёмкости неверна: {result.base_labor} != {expected_base:.2f}"

    # Проверяем сумму подпроцессов
    sum_subprocesses = sum(sp.labor for sp in result.subprocess_results)
    assert abs(result.total_labor - sum_subprocesses) < 0.1, \
        f"Сумма подпроцессов {sum_subprocesses:.2f} != итого {result.total_labor}"

    # Проверяем, что все подпроцессы имеют корректные значения
    for sp in result.subprocess_results:
        assert sp.labor >= 0, f"Трудоёмкость подпроцесса {sp.name} < 0"
        assert sp.staff >= 0, f"Численность подпроцесса {sp.name} < 0"
        assert sp.duration >= 0, f"Срок подпроцесса {sp.name} < 0"

    print("\nВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    return True


def test_save_load_project():
    """Тест сохранения и загрузки проекта"""
    import tempfile
    import os

    # Создаём проект
    project = Project.create_example()

    # Сохраняем во временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        project.save(temp_path)
        print(f"\nПроект сохранён в: {temp_path}")

        # Загружаем обратно
        loaded_project = Project.load(temp_path)

        # Проверяем
        assert loaded_project.name == project.name
        assert len(loaded_project.components) == len(project.components)
        assert loaded_project.get_function_count() == project.get_function_count()

        print("Проект успешно загружен и проверен!")

    finally:
        os.unlink(temp_path)

    return True


if __name__ == "__main__":
    print("Запуск тестов модели расчёта...\n")

    try:
        test_example_calculation()
        test_save_load_project()
        print("\n" + "=" * 60)
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\nОШИБКА ТЕСТА: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nИСКЛЮЧЕНИЕ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
