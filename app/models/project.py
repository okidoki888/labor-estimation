# -*- coding: utf-8 -*-
"""
Модель проекта для расчёта трудоёмкости
Включает сохранение/загрузку и эталонный пример
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path

from .function_catalog import get_function_by_id


@dataclass
class FunctionInstance:
    """Экземпляр функции в компоненте"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    function_id: str = ""  # ID функции из каталога
    function_name: str = ""  # Название функции
    description: str = ""  # Пользовательское описание

    # Параметры функции
    volume: int = 0  # Vi — объём в строках
    language: str = "C++"  # Средство разработки
    reuse_count: int = 1  # ri — число реализаций
    reuse_coefficient: float = 1.0  # ki — коэффициент повторного использования
    complexity_level: int = 3  # Уровень сложности (1-6)
    developer_experience: str = "Средний (3-4 ПС)"  # Опыт программистов

    def to_dict(self) -> dict:
        """Преобразовать в словарь для сохранения"""
        return {
            "id": self.id,
            "function_id": self.function_id,
            "function_name": self.function_name,
            "description": self.description,
            "volume": self.volume,
            "language": self.language,
            "reuse_count": self.reuse_count,
            "reuse_coefficient": self.reuse_coefficient,
            "complexity_level": self.complexity_level,
            "developer_experience": self.developer_experience,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FunctionInstance":
        """Создать из словаря"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            function_id=data.get("function_id", ""),
            function_name=data.get("function_name", ""),
            description=data.get("description", ""),
            volume=data.get("volume", 0),
            language=data.get("language", "C++"),
            reuse_count=data.get("reuse_count", 1),
            reuse_coefficient=data.get("reuse_coefficient", 1.0),
            complexity_level=data.get("complexity_level", 3),
            developer_experience=data.get("developer_experience", "Средний (3-4 ПС)"),
        )


@dataclass
class Component:
    """Компонент программного средства"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Новый компонент"
    description: str = ""
    functions: list[FunctionInstance] = field(default_factory=list)

    def add_function(self, func: FunctionInstance) -> None:
        """Добавить функцию в компонент"""
        self.functions.append(func)

    def remove_function(self, func_id: str) -> None:
        """Удалить функцию по ID"""
        self.functions = [f for f in self.functions if f.id != func_id]

    def to_dict(self) -> dict:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "functions": [f.to_dict() for f in self.functions],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Component":
        """Создать из словаря"""
        component = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Компонент"),
            description=data.get("description", ""),
        )
        component.functions = [
            FunctionInstance.from_dict(f) for f in data.get("functions", [])
        ]
        return component


@dataclass
class ProjectCoefficients:
    """Коэффициенты проекта для расчёта"""
    # Уровень расчёта (Таблицы 3.1-3.8)
    novelty: str = "Развитие ПС, новый тип ТС/ОС"  # K_n
    reliability: str = "Средний (восполнимый ущерб)"  # K_nad
    performance: str = "Не установлены (приемлемое время отклика)"  # K_proizv
    documentation: str = "Средний (соответствует потребностям ЖЦ)"  # K_dokum
    dev_experience: str = "Средний (3-4 ПС)"  # K_or
    structure: str = "ПС с набором библиотек"  # K_str
    interaction_technologies: list[str] = field(default_factory=list)  # K_t (множественный выбор)
    deadline: str = "≥100% от номинальной"  # K_sr_srok

    # Уровень подпроцесса — Анализ (Таблицы 4.1-4.2)
    analyst_qualification: str = "Средний"  # K_kval_an
    analyst_experience: str = "Средний (3-4 ПС)"  # K_opyt_an

    # Уровень подпроцесса — Проектирование (Таблицы 4.3-4.5)
    designer_qualification: str = "Средний"  # K_kval_pr
    designer_experience: str = "Средний (3-4 ПС)"  # K_opyt_pr
    design_tools: str = "Не использовались"  # K_sr_pr

    # Уровень подпроцесса — Программирование (Таблицы 4.6-4.7)
    programmer_qualification: str = "Средний"  # K_kval_prog
    ide: str = "Интегрированные среды (Visual Studio)"  # K_sr

    # Уровень подпроцесса — Тестирование (Таблицы 4.8-4.10)
    tester_qualification: str = "Средний"  # K_kval_test
    testing_tools: str = "Не использовались"  # K_sr_ts
    db_size: str = "Средний (10 ≤ D/P < 100)"  # K_BD

    # Уровень подпроцесса — Ввод в действие (Таблица 4.11)
    deployment_qualification: str = "Средний"  # K_kval_vn

    def to_dict(self) -> dict:
        """Преобразовать в словарь"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectCoefficients":
        """Создать из словаря"""
        return cls(
            novelty=data.get("novelty", "Развитие ПС, новый тип ТС/ОС"),
            reliability=data.get("reliability", "Средний (восполнимый ущерб)"),
            performance=data.get("performance", "Не установлены (приемлемое время отклика)"),
            documentation=data.get("documentation", "Средний (соответствует потребностям ЖЦ)"),
            dev_experience=data.get("dev_experience", "Средний (3-4 ПС)"),
            structure=data.get("structure", "ПС с набором библиотек"),
            interaction_technologies=data.get("interaction_technologies", []),
            deadline=data.get("deadline", "≥100% от номинальной"),
            analyst_qualification=data.get("analyst_qualification", "Средний"),
            analyst_experience=data.get("analyst_experience", "Средний (3-4 ПС)"),
            designer_qualification=data.get("designer_qualification", "Средний"),
            designer_experience=data.get("designer_experience", "Средний (3-4 ПС)"),
            design_tools=data.get("design_tools", "Не использовались"),
            programmer_qualification=data.get("programmer_qualification", "Средний"),
            ide=data.get("ide", "Интегрированные среды (Visual Studio)"),
            tester_qualification=data.get("tester_qualification", "Средний"),
            testing_tools=data.get("testing_tools", "Не использовались"),
            db_size=data.get("db_size", "Средний (10 ≤ D/P < 100)"),
            deployment_qualification=data.get("deployment_qualification", "Средний"),
        )


@dataclass
class Project:
    """Проект расчёта трудоёмкости"""
    name: str = "Новый проект"
    description: str = ""
    work_fund: int = 21  # Фонд рабочего времени (дней/месяц)
    constraint_type: str = "duration"  # "duration" или "staff"
    constraint_value: float = 12.0  # Значение ограничения

    components: list[Component] = field(default_factory=list)
    coefficients: ProjectCoefficients = field(default_factory=ProjectCoefficients)

    # Путь к файлу проекта
    file_path: Optional[str] = None
    modified: bool = False

    def add_component(self, component: Optional[Component] = None) -> Component:
        """Добавить компонент"""
        if component is None:
            component = Component(name=f"Компонент {len(self.components) + 1}")
        self.components.append(component)
        self.modified = True
        return component

    def remove_component(self, component_id: str) -> None:
        """Удалить компонент по ID"""
        self.components = [c for c in self.components if c.id != component_id]
        self.modified = True

    def get_component(self, component_id: str) -> Optional[Component]:
        """Получить компонент по ID"""
        for c in self.components:
            if c.id == component_id:
                return c
        return None

    def get_all_functions(self) -> list[FunctionInstance]:
        """Получить все функции из всех компонентов"""
        functions = []
        for component in self.components:
            functions.extend(component.functions)
        return functions

    def get_total_volume(self) -> int:
        """Получить общий объём (базовый, без коэффициентов)"""
        return sum(f.volume * f.reuse_count for f in self.get_all_functions())

    def get_function_count(self) -> int:
        """Получить количество функций"""
        return sum(len(c.functions) for c in self.components)

    def to_dict(self) -> dict:
        """Преобразовать проект в словарь для сохранения"""
        return {
            "name": self.name,
            "description": self.description,
            "work_fund": self.work_fund,
            "constraint_type": self.constraint_type,
            "constraint_value": self.constraint_value,
            "components": [c.to_dict() for c in self.components],
            "coefficients": self.coefficients.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Создать проект из словаря"""
        project = cls(
            name=data.get("name", "Проект"),
            description=data.get("description", ""),
            work_fund=data.get("work_fund", 21),
            constraint_type=data.get("constraint_type", "duration"),
            constraint_value=data.get("constraint_value", 12.0),
        )
        project.components = [
            Component.from_dict(c) for c in data.get("components", [])
        ]
        if "coefficients" in data:
            project.coefficients = ProjectCoefficients.from_dict(data["coefficients"])
        return project

    def save(self, file_path: Optional[str] = None) -> str:
        """Сохранить проект в JSON файл"""
        if file_path:
            self.file_path = file_path
        if not self.file_path:
            raise ValueError("Не указан путь для сохранения")

        path = Path(self.file_path)
        if not path.suffix:
            path = path.with_suffix(".json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

        self.file_path = str(path)
        self.modified = False
        return self.file_path

    @classmethod
    def load(cls, file_path: str) -> "Project":
        """Загрузить проект из JSON файла"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        project = cls.from_dict(data)
        project.file_path = file_path
        project.modified = False
        return project

    @classmethod
    def create_example(cls) -> "Project":
        """Создать эталонный пример из методики
        Программное средство мониторинга финансовых операций через банкомат
        """
        project = cls(
            name="ПС мониторинга финансовых операций через банкомат",
            description="Эталонный пример из методики СПбГУТ для проверки корректности расчётов",
            work_fund=21,
            constraint_type="duration",
            constraint_value=12.0,  # 12 месяцев
        )

        # Компонент 1: АРМ Оператора
        arm_operator = Component(name="АРМ Оператора", description="Рабочее место оператора банкомата")
        arm_operator.add_function(FunctionInstance(
            function_id="5.2.4",
            function_name="Стандартный графический UI (многооконное приложение)",
            volume=5000,
            language="C++",
            reuse_count=1,
            reuse_coefficient=1.0,
            complexity_level=3,
            developer_experience="Средний (3-4 ПС)",
        ))
        arm_operator.add_function(FunctionInstance(
            function_id="2.1.1",
            function_name="Ввод данных первичных документов в интерактивном режиме",
            volume=3000,
            language="C++",
            reuse_count=1,
            reuse_coefficient=1.0,
            complexity_level=3,
            developer_experience="Средний (3-4 ПС)",
        ))
        project.add_component(arm_operator)

        # Компонент 2: АРМ Администратора
        arm_admin = Component(name="АРМ Администратора", description="Рабочее место администратора системы")
        arm_admin.add_function(FunctionInstance(
            function_id="5.2.4",
            function_name="Стандартный графический UI (многооконное приложение)",
            volume=3000,
            language="C++",
            reuse_count=1,
            reuse_coefficient=1.0,
            complexity_level=3,
            developer_experience="Средний (3-4 ПС)",
        ))
        arm_admin.add_function(FunctionInstance(
            function_id="1.1.8",
            function_name="Создание, редактирование, удаление пользователей (группы)",
            volume=2000,
            language="C++",
            reuse_count=1,
            reuse_coefficient=1.0,
            complexity_level=3,
            developer_experience="Средний (3-4 ПС)",
        ))
        project.add_component(arm_admin)

        # Компонент 3: База Данных
        db_component = Component(name="База Данных", description="Модуль работы с базой данных")
        db_component.add_function(FunctionInstance(
            function_id="1.5.1",
            function_name="Формирование физической структуры аналитических БД (на одну БД)",
            volume=3000,
            language="C++",
            reuse_count=1,
            reuse_coefficient=1.0,
            complexity_level=3,
            developer_experience="Средний (3-4 ПС)",
        ))
        db_component.add_function(FunctionInstance(
            function_id="1.5.13",
            function_name="Обработка записей базы данных",
            volume=2000,
            language="C++",
            reuse_count=1,
            reuse_coefficient=1.0,
            complexity_level=3,
            developer_experience="Средний (3-4 ПС)",
        ))
        project.add_component(db_component)

        # Компонент 4: Отчёт
        report_component = Component(name="Отчёт", description="Модуль формирования отчётов")
        report_component.add_function(FunctionInstance(
            function_id="4.6.1",
            function_name="Формирование отчётов (на один отчёт)",
            volume=2000,
            language="C++",
            reuse_count=2,  # 2 отчёта
            reuse_coefficient=1.0,
            complexity_level=3,
            developer_experience="Средний (3-4 ПС)",
        ))
        project.add_component(report_component)

        # Компонент 5: Анализ
        analysis_component = Component(name="Анализ", description="Модуль анализа транзакций")
        analysis_component.add_function(FunctionInstance(
            function_id="2.3.1",
            function_name="Анализ безналичных расчетов",
            volume=3010,
            language="C++",
            reuse_count=1,
            reuse_coefficient=0.7,  # Частичное повторное использование
            complexity_level=4,  # Высокий
            developer_experience="Средний (3-4 ПС)",
        ))
        project.add_component(analysis_component)

        # Настройка коэффициентов для эталонного примера
        # По методике: все коэффициенты уровня расчёта = 1.00
        project.coefficients = ProjectCoefficients(
            # Уровень расчёта
            novelty="Развитие ПС, новый тип ТС/ОС",  # K_n = 1.00
            reliability="Средний (восполнимый ущерб)",  # K_nad = 1.00
            performance="Не установлены (приемлемое время отклика)",  # K_proizv = 1.00
            documentation="Средний (соответствует потребностям ЖЦ)",  # K_dokum = 1.00
            dev_experience="Средний (3-4 ПС)",  # K_or = 1.00
            structure="ПС с набором библиотек",  # K_str = 1.00
            interaction_technologies=[],  # Нет технологий — K_teh = K_str = 1.00
            deadline="≥100% от номинальной",  # K_sr_srok = 1.00

            # Подпроцессы — все средний уровень (коэфф. = 1.00)
            analyst_qualification="Средний",
            analyst_experience="Средний (3-4 ПС)",
            designer_qualification="Средний",
            designer_experience="Средний (3-4 ПС)",
            design_tools="Не использовались",
            programmer_qualification="Средний",
            ide="Интегрированные среды (Visual Studio)",
            tester_qualification="Средний",
            testing_tools="Не использовались",
            db_size="Средний (10 ≤ D/P < 100)",
            deployment_qualification="Средний",
        )

        project.modified = False
        return project
