# -*- coding: utf-8 -*-
"""
Движок расчёта трудоёмкости разработки ПС
по методике СПбГУТ
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional
from functools import reduce
import operator

from .coefficients import (
    TRANSLATION_COEFFICIENTS,
    COMPLEXITY_COEFFICIENTS,
    DEV_ENVIRONMENT_COEFFICIENTS,
    DEVELOPER_EXPERIENCE,
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

if TYPE_CHECKING:
    from .project import Project, FunctionInstance


@dataclass
class SubprocessResult:
    """Результат расчёта подпроцесса"""
    name: str
    base_coefficient: float  # A (0.01, 0.12, 0.79, 0.07, 0.01)
    coefficients: dict  # Все применённые коэффициенты
    labor: float  # Трудоёмкость T в чел.-дн.
    staff: float  # Численность N в чел.
    duration: float  # Срок t в месяцах


@dataclass
class FunctionResult:
    """Результат расчёта функции"""
    function_id: str
    function_name: str
    component_name: str
    volume_base: int  # Vi
    kp: float  # Переводной коэффициент
    reuse_count: int  # ri
    reuse_coefficient: float  # ki
    volume_corrected: float  # Vm_i = Vi * ri * ki
    k_slozhn: float  # Коэффициент сложности
    k_sr_razr: float  # Коэффициент средств разработки
    k_opyt: float  # Коэффициент опыта
    volume_adjusted: float  # Vk_i = Vm_i * K_slozhn * K_sr_razr * K_opyt


@dataclass
class CalculationResult:
    """Полный результат расчёта"""
    # Объём ПС
    total_volume: float  # V — общий объём
    functions_results: list[FunctionResult] = field(default_factory=list)

    # Базовая трудоёмкость
    A: float = 0.19  # Статистический коэффициент A
    C: float = 0.74  # Статистический коэффициент C
    k_n: float = 1.00  # Степень новизны
    k_nad: float = 1.00  # Требования к надёжности
    k_proizv: float = 1.00  # Требования к производительности
    k_dokum: float = 1.00  # Требования к документации
    k_teh: float = 1.00  # Технологии разработки
    k_or: float = 1.00  # Опыт разработки
    base_labor: float = 0.0  # T_baz

    # Подпроцессы
    subprocess_results: list[SubprocessResult] = field(default_factory=list)

    # Итоги
    total_labor: float = 0.0  # T_razr — итоговая трудоёмкость
    k_sr_srok: float = 1.00  # Влияние сроков
    final_labor: float = 0.0  # T_srok — итоговая с учётом сроков

    # Ограничения
    constraint_type: str = "duration"  # "duration" или "staff"
    constraint_value: float = 12.0  # Значение ограничения
    work_fund: int = 21  # Фонд рабочего времени (дней/месяц)

    # Рассчитанные значения
    total_duration: float = 0.0  # Общий срок в месяцах
    average_staff: float = 0.0  # Средняя численность


class CalculationEngine:
    """Движок расчёта трудоёмкости"""

    # Статистические коэффициенты
    A = 0.19
    C = 0.74

    # Коэффициенты подпроцессов
    SUBPROCESS_COEFFICIENTS = {
        "Анализ": 0.01,
        "Проектирование": 0.12,
        "Программирование": 0.79,
        "Тестирование": 0.07,
        "Ввод в действие": 0.01,
    }

    def __init__(self):
        self.result: Optional[CalculationResult] = None

    def calculate(self, project: "Project") -> CalculationResult:
        """Выполнить полный расчёт для проекта"""
        self.result = CalculationResult(total_volume=0.0)
        self.result.work_fund = project.work_fund
        self.result.constraint_type = project.constraint_type
        self.result.constraint_value = project.constraint_value

        # 1. Расчёт объёма ПС
        self._calculate_volume(project)

        # 2. Расчёт базовой трудоёмкости
        self._calculate_base_labor(project)

        # 3. Расчёт подпроцессов
        self._calculate_subprocesses(project)

        # 4. Расчёт итоговой трудоёмкости
        self._calculate_totals(project)

        return self.result

    def _calculate_volume(self, project: "Project") -> None:
        """Расчёт объёма ПС (формулы 3.3-3.5)"""
        total_volume = 0.0

        for component in project.components:
            for func in component.functions:
                # Получаем коэффициенты
                kp = TRANSLATION_COEFFICIENTS.get(func.language, 1.00)
                k_slozhn = COMPLEXITY_COEFFICIENTS.get(func.complexity_level, 1.00)
                k_sr_razr = DEV_ENVIRONMENT_COEFFICIENTS.get(func.language, 1.00)
                k_opyt = DEVELOPER_EXPERIENCE.get(func.developer_experience, 1.00)

                # Формула 3.3: Vm_i = Vi * ri * ki
                volume_corrected = func.volume * func.reuse_count * func.reuse_coefficient

                # Формула 3.4: Vk_i = Vm_i * K_slozhn * K_sr_razr * K_opyt
                volume_adjusted = volume_corrected * k_slozhn * k_sr_razr * k_opyt

                # Сохраняем результат для функции
                func_result = FunctionResult(
                    function_id=func.function_id,
                    function_name=func.function_name,
                    component_name=component.name,
                    volume_base=func.volume,
                    kp=kp,
                    reuse_count=func.reuse_count,
                    reuse_coefficient=func.reuse_coefficient,
                    volume_corrected=round(volume_corrected, 2),
                    k_slozhn=k_slozhn,
                    k_sr_razr=k_sr_razr,
                    k_opyt=k_opyt,
                    volume_adjusted=round(volume_adjusted, 2),
                )
                self.result.functions_results.append(func_result)

                # Формула 3.5: V = Σ Vk_j
                total_volume += volume_adjusted

        self.result.total_volume = round(total_volume, 2)

    def _calculate_base_labor(self, project: "Project") -> None:
        """Расчёт базовой трудоёмкости (формулы 3.6-3.7)"""
        coeffs = project.coefficients

        # Получаем коэффициенты уровня расчёта
        k_n = NOVELTY_COEFFICIENTS.get(coeffs.novelty, 1.00)
        k_nad = RELIABILITY_COEFFICIENTS.get(coeffs.reliability, 1.00)
        k_proizv = PERFORMANCE_COEFFICIENTS.get(coeffs.performance, 1.00)
        k_dokum = DOCUMENTATION_COEFFICIENTS.get(coeffs.documentation, 1.00)
        k_or = DEVELOPMENT_EXPERIENCE.get(coeffs.dev_experience, 1.00)

        # Формула 3.7: K_teh = K_str * Π(K_t_i)
        k_str = STRUCTURE_COEFFICIENTS.get(coeffs.structure, 1.00)

        # Если выбраны технологии взаимодействия
        if coeffs.interaction_technologies:
            k_t_values = [
                INTERACTION_TECHNOLOGIES.get(tech, 1.00)
                for tech in coeffs.interaction_technologies
            ]
            k_t_product = reduce(operator.mul, k_t_values, 1.0)
        else:
            k_t_product = 1.0

        k_teh = k_str * k_t_product

        # Сохраняем коэффициенты
        self.result.k_n = k_n
        self.result.k_nad = k_nad
        self.result.k_proizv = k_proizv
        self.result.k_dokum = k_dokum
        self.result.k_teh = round(k_teh, 4)
        self.result.k_or = k_or

        # Формула 3.6: T_baz = A * V^C * K_n * K_nad * K_proizv * K_dokum * K_teh * K_or
        V = self.result.total_volume
        if V > 0:
            base_labor = (
                self.A *
                (V ** self.C) *
                k_n * k_nad * k_proizv * k_dokum * k_teh * k_or
            )
        else:
            base_labor = 0.0

        self.result.base_labor = round(base_labor, 2)

    def _calculate_subprocesses(self, project: "Project") -> None:
        """Расчёт трудоёмкостей подпроцессов (формулы 3.8-3.12)"""
        coeffs = project.coefficients
        T_baz = self.result.base_labor
        work_fund = project.work_fund

        # Определяем ограничение
        if project.constraint_type == "duration":
            total_duration = project.constraint_value
        else:
            total_duration = None  # Будем рассчитывать

        subprocess_results = []

        # 1. Анализ (формула 3.8)
        k_kval_an = ANALYST_QUALIFICATION.get(coeffs.analyst_qualification, 1.00)
        k_opyt_an = ANALYST_EXPERIENCE.get(coeffs.analyst_experience, 1.00)
        T1 = T_baz * 0.01 * k_kval_an * k_opyt_an
        subprocess_results.append(self._create_subprocess_result(
            "Анализ", 0.01, T1, work_fund, total_duration, project.constraint_value,
            {"K_kval_an": k_kval_an, "K_opyt_an": k_opyt_an}
        ))

        # 2. Проектирование (формула 3.9)
        k_kval_pr = DESIGNER_QUALIFICATION.get(coeffs.designer_qualification, 1.00)
        k_opyt_pr = DESIGNER_EXPERIENCE.get(coeffs.designer_experience, 1.00)
        k_sr_pr = DESIGN_TOOLS.get(coeffs.design_tools, 1.00)
        T2 = T_baz * 0.12 * k_kval_pr * k_opyt_pr * k_sr_pr
        subprocess_results.append(self._create_subprocess_result(
            "Проектирование", 0.12, T2, work_fund, total_duration, project.constraint_value,
            {"K_kval_pr": k_kval_pr, "K_opyt_pr": k_opyt_pr, "K_sr_pr": k_sr_pr}
        ))

        # 3. Программирование (формула 3.10)
        k_kval_prog = PROGRAMMER_QUALIFICATION.get(coeffs.programmer_qualification, 1.00)
        k_sr = IDE_COEFFICIENTS.get(coeffs.ide, 1.00)
        T3 = T_baz * 0.79 * k_kval_prog * k_sr
        subprocess_results.append(self._create_subprocess_result(
            "Программирование", 0.79, T3, work_fund, total_duration, project.constraint_value,
            {"K_kval_prog": k_kval_prog, "K_sr": k_sr}
        ))

        # 4. Тестирование (формула 3.11)
        k_kval_test = TESTER_QUALIFICATION.get(coeffs.tester_qualification, 1.00)
        k_sr_ts = TESTING_TOOLS.get(coeffs.testing_tools, 1.00)
        k_bd = DB_SIZE.get(coeffs.db_size, 1.00)
        T4 = T_baz * 0.07 * k_kval_test * k_sr_ts * k_bd
        subprocess_results.append(self._create_subprocess_result(
            "Тестирование", 0.07, T4, work_fund, total_duration, project.constraint_value,
            {"K_kval_test": k_kval_test, "K_sr_ts": k_sr_ts, "K_BD": k_bd}
        ))

        # 5. Ввод в действие (формула 3.12)
        k_kval_vn = DEPLOYMENT_QUALIFICATION.get(coeffs.deployment_qualification, 1.00)
        T5 = T_baz * 0.01 * k_kval_vn
        subprocess_results.append(self._create_subprocess_result(
            "Ввод в действие", 0.01, T5, work_fund, total_duration, project.constraint_value,
            {"K_kval_vn": k_kval_vn}
        ))

        self.result.subprocess_results = subprocess_results

    def _create_subprocess_result(
        self,
        name: str,
        base_coef: float,
        labor: float,
        work_fund: int,
        total_duration: Optional[float],
        constraint_value: float,
        coefficients: dict
    ) -> SubprocessResult:
        """Создать результат подпроцесса с расчётом численности и сроков"""
        labor = round(labor, 2)

        if total_duration:
            # Ограничение по продолжительности - рассчитываем численность
            # Распределяем срок пропорционально базовому коэффициенту
            duration = total_duration * base_coef / (0.01 + 0.12 + 0.79 + 0.07 + 0.01)
            # Формула 4.3: N = T / (t * Ф)
            if duration > 0:
                staff = labor / (duration * work_fund)
            else:
                staff = 0.0
        else:
            # Ограничение по численности - рассчитываем срок
            staff = constraint_value
            # Формула 4.1: t = T / (N * Ф)
            if staff > 0:
                duration = labor / (staff * work_fund)
            else:
                duration = 0.0

        return SubprocessResult(
            name=name,
            base_coefficient=base_coef,
            coefficients=coefficients,
            labor=labor,
            staff=round(staff, 2),
            duration=round(duration, 2),
        )

    def _calculate_totals(self, project: "Project") -> None:
        """Расчёт итоговых показателей (формулы 3.13-3.14, 4.1-4.3)"""
        coeffs = project.coefficients

        # Формула 3.13: T_razr = T1 + T2 + T3 + T4 + T5
        total_labor = sum(sp.labor for sp in self.result.subprocess_results)
        self.result.total_labor = round(total_labor, 2)

        # Коэффициент сокращения сроков
        k_sr_srok = DEADLINE_COEFFICIENTS.get(coeffs.deadline, 1.00)
        self.result.k_sr_srok = k_sr_srok

        # Формула 3.14: T_srok = T_razr * K_sr_srok
        self.result.final_labor = round(total_labor * k_sr_srok, 2)

        # Расчёт общей продолжительности и средней численности
        if project.constraint_type == "duration":
            self.result.total_duration = project.constraint_value
            if project.constraint_value > 0:
                self.result.average_staff = round(
                    self.result.final_labor / (project.constraint_value * project.work_fund), 2
                )
        else:
            self.result.average_staff = project.constraint_value
            if project.constraint_value > 0 and project.work_fund > 0:
                self.result.total_duration = round(
                    self.result.final_labor / (project.constraint_value * project.work_fund), 2
                )
