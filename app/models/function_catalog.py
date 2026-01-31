# -*- coding: utf-8 -*-
"""
Каталог функций программных средств (Приложение 1, Таблица 1.1)
по методике СПбГУТ
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OperationType(Enum):
    """Типы операций для определения таблицы сложности (2.1-2.5)"""
    CONTROL = "Управляющие операции"  # Таблица 2.1
    COMPUTATIONAL = "Вычислительные операции"  # Таблица 2.2
    HARDWARE_DEPENDENT = "Операции, зависящие от аппаратуры"  # Таблица 2.3
    DATA_MANAGEMENT = "Операции управления данными"  # Таблица 2.4
    USER_INTERFACE = "Операции управления пользовательского интерфейса"  # Таблица 2.5


class FunctionType(Enum):
    """Тип функции"""
    ATOMIC = "atomic"  # * - атомарная функция
    COMPOSITE = "composite"  # ** - составная функция
    STRUCTURAL = "structural"  # Структурная функция


@dataclass
class FunctionInfo:
    """Информация о функции из каталога"""
    id: str  # Номер функции (например, "1.1.1")
    name: str  # Наименование функции
    operation_type: OperationType  # Тип операции
    volume_min: int  # Минимальный объём в строках
    volume_max: int  # Максимальный объём в строках
    function_type: FunctionType = FunctionType.STRUCTURAL  # Тип функции
    category: str = ""  # Категория (подраздел)

    @property
    def volume_range(self) -> str:
        """Диапазон объёма как строка"""
        if self.volume_min == self.volume_max:
            return str(self.volume_min)
        return f"{self.volume_min}–{self.volume_max}"

    @property
    def default_volume(self) -> int:
        """Среднее значение объёма по умолчанию"""
        return (self.volume_min + self.volume_max) // 2

    @property
    def type_marker(self) -> str:
        """Маркер типа функции для отображения"""
        if self.function_type == FunctionType.ATOMIC:
            return "*"
        elif self.function_type == FunctionType.COMPOSITE:
            return "**"
        return ""


# Полный каталог функций
FUNCTION_CATALOG: list[FunctionInfo] = [
    # =============================================================================
    # 1. УПРАВЛЯЮЩИЕ ОПЕРАЦИИ
    # =============================================================================

    # 1.1. Информационная безопасность
    FunctionInfo("1.1.1", "Реализация криптографических алгоритмов (один алгоритм)",
                 OperationType.CONTROL, 100, 1000, FunctionType.ATOMIC, "Информационная безопасность"),
    FunctionInfo("1.1.2", "Обеспечение безопасности передачи сообщений и обмена данными (шифрование)",
                 OperationType.CONTROL, 200, 1500, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.3", "Организация криптозащиты с помощью ПТК Криптоцентр авизо",
                 OperationType.CONTROL, 5000, 6000, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.4", "Контроль целостности ПО",
                 OperationType.CONTROL, 2500, 3500, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.5", "Реализация базовых функций информационной безопасности",
                 OperationType.CONTROL, 6000, 15000, FunctionType.COMPOSITE, "Информационная безопасность"),
    FunctionInfo("1.1.6", "Поддержка дискреционного контроля доступа",
                 OperationType.CONTROL, 2000, 5000, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.7", "Поддержка мандатного контроля доступа",
                 OperationType.CONTROL, 2000, 5000, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.8", "Создание, редактирование, удаление пользователей (группы)",
                 OperationType.CONTROL, 1500, 5000, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.9", "Установка прав доступа к объекту",
                 OperationType.CONTROL, 1000, 2000, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.10", "Ведение протокола доступа",
                 OperationType.CONTROL, 2000, 4000, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.11", "Настройка политики безопасности",
                 OperationType.CONTROL, 1000, 2000, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.12", "Ведение журналов отказа",
                 OperationType.CONTROL, 1000, 1500, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.13", "Взаимодействие с ПО Верба-OW, САЭД",
                 OperationType.CONTROL, 200, 500, FunctionType.STRUCTURAL, "Информационная безопасность"),
    FunctionInfo("1.1.14", "Взаимодействие с ПО СКАД «Сигнатура»",
                 OperationType.CONTROL, 200, 1000, FunctionType.STRUCTURAL, "Информационная безопасность"),

    # 1.2. Реализация интерфейсов между программными средствами
    FunctionInfo("1.2.1", "Взаимодействие с другим ПО",
                 OperationType.CONTROL, 500, 1000, FunctionType.STRUCTURAL, "Интерфейсы между ПС"),
    FunctionInfo("1.2.2", "Взаимодействие с транспортной (почтовой) системой",
                 OperationType.CONTROL, 2000, 3000, FunctionType.STRUCTURAL, "Интерфейсы между ПС"),
    FunctionInfo("1.2.3", "Реализация ПО обмена информацией между ЦОИ и клиентами (WEB-сервер)",
                 OperationType.CONTROL, 9000, 10000, FunctionType.COMPOSITE, "Интерфейсы между ПС"),
    FunctionInfo("1.2.4", "Организация доступа к динамическим информационным ресурсам через Intranet",
                 OperationType.CONTROL, 10000, 15000, FunctionType.COMPOSITE, "Интерфейсы между ПС"),
    FunctionInfo("1.2.5", "Организация регулярно актуализируемого статистического контента",
                 OperationType.CONTROL, 10000, 15000, FunctionType.COMPOSITE, "Интерфейсы между ПС"),

    # 1.3. Выполнение регламентных операций
    FunctionInfo("1.3.1", "Пусковое решение",
                 OperationType.CONTROL, 500, 1000, FunctionType.STRUCTURAL, "Регламентные операции"),
    FunctionInfo("1.3.2", "Регламентные операции: открытие и закрытие операционного дня",
                 OperationType.CONTROL, 4000, 5000, FunctionType.STRUCTURAL, "Регламентные операции"),
    FunctionInfo("1.3.3", "Операционный день",
                 OperationType.CONTROL, 10000, 15000, FunctionType.STRUCTURAL, "Регламентные операции"),
    FunctionInfo("1.3.4", "Реализация процедур обновления версий ПО",
                 OperationType.CONTROL, 1000, 2000, FunctionType.STRUCTURAL, "Регламентные операции"),

    # 1.4. Реализация взаимосвязи ПС и компонентов
    FunctionInfo("1.4.1", "Сетевая передача команд и сообщений",
                 OperationType.CONTROL, 100, 1000, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.2", "Реализация связи между распределенными приложениями (стандартные транспортные средства)",
                 OperationType.CONTROL, 100, 1000, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.3", "Реализация связи между распред. приложениями (сетевые интерфейсы низкого уровня)",
                 OperationType.CONTROL, 200, 500, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.4", "Удаленная доставка информации с подтверждением получения",
                 OperationType.CONTROL, 200, 500, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.5", "Вызов удаленных процедур (единичный вызов)",
                 OperationType.CONTROL, 500, 1000, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.6", "Управление файлами и передачей между удалёнными файловыми системами",
                 OperationType.CONTROL, 200, 500, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.7", "Обработка сообщений",
                 OperationType.CONTROL, 10, 200, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.8", "Обработка распределенных транзакций",
                 OperationType.CONTROL, 10, 300, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.9", "Реализация средства контроля состояния распределенной сети",
                 OperationType.CONTROL, 100, 200, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.10", "Доступ к общей памяти (одна машина)",
                 OperationType.CONTROL, 10, 50, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.11", "Доступ к общей памяти (вычислительная сеть)",
                 OperationType.CONTROL, 10, 200, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),
    FunctionInfo("1.4.12", "Ведение журнала обращений к распределённому ПС",
                 OperationType.CONTROL, 10, 500, FunctionType.STRUCTURAL, "Взаимосвязь ПС"),

    # 1.5. Создание и поддержка аналитических БД
    FunctionInfo("1.5.1", "Формирование физической структуры аналитических БД (на одну БД)",
                 OperationType.CONTROL, 1000, 8000, FunctionType.STRUCTURAL, "Аналитические БД"),
    FunctionInfo("1.5.2", "Формирование многомерной структуры аналитических БД (на одну БД)",
                 OperationType.CONTROL, 1000, 8000, FunctionType.STRUCTURAL, "Аналитические БД"),
    FunctionInfo("1.5.3", "Описание связей между аналитическими базами данных",
                 OperationType.CONTROL, 1500, 2000, FunctionType.STRUCTURAL, "Аналитические БД"),
    FunctionInfo("1.5.4", "Формирование запросов к аналитическим БД (один запрос)",
                 OperationType.CONTROL, 10, 80, FunctionType.ATOMIC, "Аналитические БД"),
    FunctionInfo("1.5.5", "Ведение журнала операций с аналитическими БД",
                 OperationType.CONTROL, 1000, 2000, FunctionType.STRUCTURAL, "Аналитические БД"),
    FunctionInfo("1.5.6", "Формирование ETL-процедур",
                 OperationType.CONTROL, 2000, 15000, FunctionType.STRUCTURAL, "Аналитические БД"),
    FunctionInfo("1.5.7", "Протоколирование ETL-процедур",
                 OperationType.CONTROL, 2500, 5000, FunctionType.STRUCTURAL, "Аналитические БД"),
    FunctionInfo("1.5.8", "Функции настройки аналитических БД",
                 OperationType.CONTROL, 1500, 2000, FunctionType.STRUCTURAL, "Аналитические БД"),
    FunctionInfo("1.5.9", "Модификация аналитических БД (один запрос)",
                 OperationType.CONTROL, 50, 400, FunctionType.ATOMIC, "Аналитические БД"),
    FunctionInfo("1.5.10", "Контроль целостности и восстановление аналитических БД",
                 OperationType.CONTROL, 500, 1000, FunctionType.STRUCTURAL, "Аналитические БД"),
    FunctionInfo("1.5.11", "Прикладное администрирование аналитических БД",
                 OperationType.CONTROL, 1000, 5000, FunctionType.COMPOSITE, "Аналитические БД"),
    FunctionInfo("1.5.12", "Поиск, предоставление и вывод информации",
                 OperationType.CONTROL, 1000, 6000, FunctionType.STRUCTURAL, "Аналитические БД"),
    FunctionInfo("1.5.13", "Обработка записей базы данных",
                 OperationType.CONTROL, 500, 3000, FunctionType.STRUCTURAL, "Аналитические БД"),

    # =============================================================================
    # 2. ВЫЧИСЛИТЕЛЬНЫЕ ОПЕРАЦИИ
    # =============================================================================

    # 2.1. Ввод и обработка данных
    FunctionInfo("2.1.1", "Ввод данных первичных документов в интерактивном режиме",
                 OperationType.COMPUTATIONAL, 2000, 9000, FunctionType.STRUCTURAL, "Ввод и обработка данных"),
    FunctionInfo("2.1.2", "Ввод данных по нарушениям в интерактивном режиме",
                 OperationType.COMPUTATIONAL, 2000, 4000, FunctionType.STRUCTURAL, "Ввод и обработка данных"),
    FunctionInfo("2.1.3", "Ввод и первичный контроль документов из файлов",
                 OperationType.COMPUTATIONAL, 1500, 6000, FunctionType.STRUCTURAL, "Ввод и обработка данных"),
    FunctionInfo("2.1.4", "Логический, синтаксический и номенклатурный контроль данных",
                 OperationType.COMPUTATIONAL, 1500, 6000, FunctionType.STRUCTURAL, "Ввод и обработка данных"),
    FunctionInfo("2.1.5", "Расчет алгебраических выражений",
                 OperationType.COMPUTATIONAL, 100, 1000, FunctionType.STRUCTURAL, "Ввод и обработка данных"),
    FunctionInfo("2.1.6", "Статистическая обработка данных",
                 OperationType.COMPUTATIONAL, 2000, 5000, FunctionType.STRUCTURAL, "Ввод и обработка данных"),
    FunctionInfo("2.1.7", "Обработка документов (различные типы)",
                 OperationType.COMPUTATIONAL, 1500, 10000, FunctionType.STRUCTURAL, "Ввод и обработка данных"),
    FunctionInfo("2.1.15", "Ввод прочих данных",
                 OperationType.COMPUTATIONAL, 1000, 4000, FunctionType.STRUCTURAL, "Ввод и обработка данных"),
    FunctionInfo("2.1.16", "Обработка входной информации (прочих данных)",
                 OperationType.COMPUTATIONAL, 1500, 6000, FunctionType.STRUCTURAL, "Ввод и обработка данных"),

    # 2.2. Составление и анализ балансов
    FunctionInfo("2.2.1", "Составление балансов",
                 OperationType.COMPUTATIONAL, 500, 1000, FunctionType.COMPOSITE, "Составление и анализ балансов"),
    FunctionInfo("2.2.2", "Анализ балансов",
                 OperationType.COMPUTATIONAL, 1000, 3500, FunctionType.COMPOSITE, "Составление и анализ балансов"),
    FunctionInfo("2.2.3", "Выполнение баланса и оборотов КО за месяц",
                 OperationType.COMPUTATIONAL, 2500, 3500, FunctionType.COMPOSITE, "Составление и анализ балансов"),
    FunctionInfo("2.2.4", "Выполнение ежедневного баланса",
                 OperationType.COMPUTATIONAL, 1500, 2000, FunctionType.COMPOSITE, "Составление и анализ балансов"),
    FunctionInfo("2.2.5", "Корректировка балансов",
                 OperationType.COMPUTATIONAL, 200, 500, FunctionType.COMPOSITE, "Составление и анализ балансов"),
    FunctionInfo("2.2.6", "Пересчёт балансов",
                 OperationType.COMPUTATIONAL, 2000, 3000, FunctionType.COMPOSITE, "Составление и анализ балансов"),

    # 2.3. Проведение экономического анализа
    FunctionInfo("2.3.1", "Анализ безналичных расчетов",
                 OperationType.COMPUTATIONAL, 300, 8000, FunctionType.COMPOSITE, "Экономический анализ"),
    FunctionInfo("2.3.2", "Анализ денежной массы",
                 OperationType.COMPUTATIONAL, 300, 8000, FunctionType.COMPOSITE, "Экономический анализ"),
    FunctionInfo("2.3.3", "Анализ валютных курсов",
                 OperationType.COMPUTATIONAL, 300, 8000, FunctionType.COMPOSITE, "Экономический анализ"),
    FunctionInfo("2.3.4", "Анализ кредитных операций",
                 OperationType.COMPUTATIONAL, 300, 8000, FunctionType.COMPOSITE, "Экономический анализ"),
    FunctionInfo("2.3.5", "Прочий экономический анализ",
                 OperationType.COMPUTATIONAL, 300, 8000, FunctionType.COMPOSITE, "Экономический анализ"),

    # 2.4. Выполнение задач планирования
    FunctionInfo("2.4.1", "Планирование инспекторских проверок",
                 OperationType.COMPUTATIONAL, 1500, 2000, FunctionType.COMPOSITE, "Задачи планирования"),
    FunctionInfo("2.4.2", "Планирование эмиссии",
                 OperationType.COMPUTATIONAL, 4000, 5000, FunctionType.COMPOSITE, "Задачи планирования"),
    FunctionInfo("2.4.3", "Планирование прочих задач",
                 OperationType.COMPUTATIONAL, 800, 4000, FunctionType.COMPOSITE, "Задачи планирования"),

    # 2.5. Мониторинг
    FunctionInfo("2.5.1", "Мониторинг отчётности КО",
                 OperationType.COMPUTATIONAL, 6000, 7000, FunctionType.COMPOSITE, "Мониторинг"),
    FunctionInfo("2.5.2", "Мониторинг отчётности ТУ",
                 OperationType.COMPUTATIONAL, 6000, 7000, FunctionType.COMPOSITE, "Мониторинг"),

    # 2.6. Формирование и обработка аналитических показателей
    FunctionInfo("2.6.1", "Расчёт экономических показателей",
                 OperationType.COMPUTATIONAL, 5000, 15000, FunctionType.COMPOSITE, "Аналитические показатели"),
    FunctionInfo("2.6.2", "Экономический и финансовый анализ",
                 OperationType.COMPUTATIONAL, 10000, 20000, FunctionType.COMPOSITE, "Аналитические показатели"),
    FunctionInfo("2.6.3", "Моделирование и прогнозирование",
                 OperationType.COMPUTATIONAL, 20000, 30000, FunctionType.COMPOSITE, "Аналитические показатели"),

    # =============================================================================
    # 3. ОПЕРАЦИИ, ЗАВИСЯЩИЕ ОТ АППАРАТУРЫ
    # =============================================================================

    # 3.1. Приём документов от различных источников
    FunctionInfo("3.1.1", "Приём файлов, первичный контроль",
                 OperationType.HARDWARE_DEPENDENT, 300, 1500, FunctionType.STRUCTURAL, "Приём документов"),
    FunctionInfo("3.1.2", "Приём информации из ЦОИ",
                 OperationType.HARDWARE_DEPENDENT, 2000, 8000, FunctionType.STRUCTURAL, "Приём документов"),
    FunctionInfo("3.1.3", "Приём данных, содержащихся в DBF файлах",
                 OperationType.HARDWARE_DEPENDENT, 200, 1200, FunctionType.STRUCTURAL, "Приём документов"),
    FunctionInfo("3.1.4", "Приём описи к конвертам с документами",
                 OperationType.HARDWARE_DEPENDENT, 1500, 2000, FunctionType.STRUCTURAL, "Приём документов"),
    FunctionInfo("3.1.5", "Приём текстовых файлов",
                 OperationType.HARDWARE_DEPENDENT, 300, 800, FunctionType.STRUCTURAL, "Приём документов"),

    # 3.2. Регистрация входных документов
    FunctionInfo("3.2.1", "Регистрация входных документов",
                 OperationType.HARDWARE_DEPENDENT, 500, 1000, FunctionType.STRUCTURAL, "Регистрация документов"),
    FunctionInfo("3.2.2", "Регистрация исходящих авизо",
                 OperationType.HARDWARE_DEPENDENT, 2500, 3000, FunctionType.STRUCTURAL, "Регистрация документов"),
    FunctionInfo("3.2.3", "Регистрация телеграфных и почтовых авизо",
                 OperationType.HARDWARE_DEPENDENT, 1000, 1500, FunctionType.STRUCTURAL, "Регистрация документов"),

    # 3.3. Работа с файлами и форматами
    FunctionInfo("3.3.1", "Загрузка файлов",
                 OperationType.HARDWARE_DEPENDENT, 1000, 1500, FunctionType.STRUCTURAL, "Работа с файлами"),
    FunctionInfo("3.3.2", "Преобразование формата данных",
                 OperationType.HARDWARE_DEPENDENT, 1000, 4500, FunctionType.STRUCTURAL, "Работа с файлами"),
    FunctionInfo("3.3.3", "Формирование файлов",
                 OperationType.HARDWARE_DEPENDENT, 500, 3000, FunctionType.STRUCTURAL, "Работа с файлами"),

    # 3.4. Ведение архива и копирование информации
    FunctionInfo("3.4.1", "Создание архива",
                 OperationType.HARDWARE_DEPENDENT, 500, 2500, FunctionType.STRUCTURAL, "Ведение архива"),
    FunctionInfo("3.4.2", "Добавление данных в архив",
                 OperationType.HARDWARE_DEPENDENT, 500, 1000, FunctionType.STRUCTURAL, "Ведение архива"),
    FunctionInfo("3.4.3", "Извлечение данных из архива",
                 OperationType.HARDWARE_DEPENDENT, 500, 1000, FunctionType.STRUCTURAL, "Ведение архива"),
    FunctionInfo("3.4.4", "Поиск данных в архиве",
                 OperationType.HARDWARE_DEPENDENT, 500, 1500, FunctionType.STRUCTURAL, "Ведение архива"),
    FunctionInfo("3.4.5", "Проверка целостности архива",
                 OperationType.HARDWARE_DEPENDENT, 500, 1500, FunctionType.STRUCTURAL, "Ведение архива"),
    FunctionInfo("3.4.6", "Задачи ведения электронного архива",
                 OperationType.HARDWARE_DEPENDENT, 2500, 7500, FunctionType.COMPOSITE, "Ведение архива"),

    # =============================================================================
    # 4. ОПЕРАЦИИ УПРАВЛЕНИЯ ДАННЫМИ
    # =============================================================================

    # 4.1. Ведение журналов
    FunctionInfo("4.1.1", "Ведение журналов (на один журнал)",
                 OperationType.DATA_MANAGEMENT, 500, 5000, FunctionType.ATOMIC, "Ведение журналов"),
    FunctionInfo("4.1.2", "Ведение журнала регистрации запросов и подтверждений по авизо",
                 OperationType.DATA_MANAGEMENT, 2000, 5000, FunctionType.STRUCTURAL, "Ведение журналов"),
    FunctionInfo("4.1.3", "Вывод журналов приёма-передачи",
                 OperationType.DATA_MANAGEMENT, 500, 800, FunctionType.STRUCTURAL, "Ведение журналов"),
    FunctionInfo("4.1.4", "Контроль и журнализация доступа к защищённым ресурсам",
                 OperationType.DATA_MANAGEMENT, 1500, 2000, FunctionType.STRUCTURAL, "Ведение журналов"),

    # 4.2. Работа со справочниками
    FunctionInfo("4.2.1", "Ведение справочников (на один справочник)",
                 OperationType.DATA_MANAGEMENT, 500, 3000, FunctionType.ATOMIC, "Работа со справочниками"),
    FunctionInfo("4.2.2", "Ведение книги регистрации открытых лицевых счетов",
                 OperationType.DATA_MANAGEMENT, 10000, 10800, FunctionType.STRUCTURAL, "Работа со справочниками"),

    # 4.3. Контроль информации документов
    FunctionInfo("4.3.1", "Контроль входной информации документов",
                 OperationType.DATA_MANAGEMENT, 500, 2000, FunctionType.STRUCTURAL, "Контроль документов"),
    FunctionInfo("4.3.2", "Контроль информации при вводе данных документа (на форму ввода)",
                 OperationType.DATA_MANAGEMENT, 300, 400, FunctionType.ATOMIC, "Контроль документов"),

    # 4.4. Настройка ПС
    FunctionInfo("4.4.1", "Разработка и ввод метаданных",
                 OperationType.DATA_MANAGEMENT, 1000, 8000, FunctionType.STRUCTURAL, "Настройка ПС"),

    # 4.5. Ведение и обработка протоколов
    FunctionInfo("4.5.1", "Протоколирование работы",
                 OperationType.DATA_MANAGEMENT, 2500, 3500, FunctionType.STRUCTURAL, "Ведение протоколов"),
    FunctionInfo("4.5.2", "Ведение протокола выполнения расчётов",
                 OperationType.DATA_MANAGEMENT, 500, 700, FunctionType.STRUCTURAL, "Ведение протоколов"),
    FunctionInfo("4.5.3", "Формирование протокола проводок",
                 OperationType.DATA_MANAGEMENT, 700, 1500, FunctionType.STRUCTURAL, "Ведение протоколов"),
    FunctionInfo("4.5.4", "Обработка протоколов",
                 OperationType.DATA_MANAGEMENT, 1000, 2000, FunctionType.STRUCTURAL, "Ведение протоколов"),

    # 4.6. Формирование отчётов
    FunctionInfo("4.6.1", "Формирование отчётов (на один отчёт)",
                 OperationType.DATA_MANAGEMENT, 100, 4000, FunctionType.ATOMIC, "Формирование отчётов"),
    FunctionInfo("4.6.2", "Просмотр и редактирование отчётных форм",
                 OperationType.DATA_MANAGEMENT, 500, 1000, FunctionType.STRUCTURAL, "Формирование отчётов"),
    FunctionInfo("4.6.3", "Подготовка форм отчётности (на одну форму)",
                 OperationType.DATA_MANAGEMENT, 1000, 3000, FunctionType.ATOMIC, "Формирование отчётов"),

    # 4.7. Распределённая обработка данных
    FunctionInfo("4.7.1", "Создание одного объекта на базе технологии CORBA",
                 OperationType.DATA_MANAGEMENT, 50, 50, FunctionType.ATOMIC, "Распределённая обработка"),
    FunctionInfo("4.7.2", "Создание одного объекта на базе технологии COM",
                 OperationType.DATA_MANAGEMENT, 60, 60, FunctionType.ATOMIC, "Распределённая обработка"),
    FunctionInfo("4.7.3", "Вызов метода CORBA-объекта (один вызов)",
                 OperationType.DATA_MANAGEMENT, 2, 2, FunctionType.ATOMIC, "Распределённая обработка"),
    FunctionInfo("4.7.4", "Вызов метода COM-объекта (один вызов)",
                 OperationType.DATA_MANAGEMENT, 1, 1, FunctionType.ATOMIC, "Распределённая обработка"),
    FunctionInfo("4.7.5", "Реализация сетевого взаимодействия Sockets API (сервер)",
                 OperationType.DATA_MANAGEMENT, 40, 40, FunctionType.ATOMIC, "Распределённая обработка"),
    FunctionInfo("4.7.6", "Реализация сетевого взаимодействия Sockets API (клиент)",
                 OperationType.DATA_MANAGEMENT, 20, 20, FunctionType.ATOMIC, "Распределённая обработка"),

    # 4.8. Ведение синтетического и аналитического учёта
    FunctionInfo("4.8.1", "Отражение операций по лицевым счетам аналитического учёта",
                 OperationType.DATA_MANAGEMENT, 28000, 28000, FunctionType.STRUCTURAL, "Ведение учёта"),
    FunctionInfo("4.8.2", "Ведение синтетического учёта совершаемых операций",
                 OperationType.DATA_MANAGEMENT, 16875, 16875, FunctionType.STRUCTURAL, "Ведение учёта"),

    # =============================================================================
    # 5. ОПЕРАЦИИ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА
    # =============================================================================

    # 5.1. Настройка ПС на условия применения
    FunctionInfo("5.1.1", "Настройка параметров",
                 OperationType.USER_INTERFACE, 500, 1000, FunctionType.STRUCTURAL, "Настройка ПС"),
    FunctionInfo("5.1.2", "Настройка аналитических таблиц",
                 OperationType.USER_INTERFACE, 1000, 2000, FunctionType.STRUCTURAL, "Настройка ПС"),

    # 5.2. Реализация пользовательского интерфейса
    FunctionInfo("5.2.1", "Реализация интерфейса пользователя",
                 OperationType.USER_INTERFACE, 20, 5000, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.2", "Стандартный графический UI (однооконное приложение)",
                 OperationType.USER_INTERFACE, 300, 2000, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.3", "Стандартный графический UI (диалоговое приложение)",
                 OperationType.USER_INTERFACE, 20, 1000, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.4", "Стандартный графический UI (многооконное приложение)",
                 OperationType.USER_INTERFACE, 500, 7000, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.5", "Однооконное приложение с использованием API",
                 OperationType.USER_INTERFACE, 1000, 2000, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.6", "Однооконное приложение с использованием MFC/OWL",
                 OperationType.USER_INTERFACE, 600, 900, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.7", "Однооконное приложение с использованием VCL",
                 OperationType.USER_INTERFACE, 300, 700, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.8", "Диалоговое приложение с использованием API",
                 OperationType.USER_INTERFACE, 500, 1000, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.9", "Диалоговое приложение с использованием MFC/OWL",
                 OperationType.USER_INTERFACE, 40, 100, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.10", "Диалоговое приложение с использованием VCL",
                 OperationType.USER_INTERFACE, 20, 100, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.11", "Многооконное приложение с использованием API",
                 OperationType.USER_INTERFACE, 2000, 7000, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.12", "Многооконное приложение с использованием MFC/OWL",
                 OperationType.USER_INTERFACE, 600, 1500, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.13", "Многооконное приложение с использованием VCL",
                 OperationType.USER_INTERFACE, 500, 1500, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),
    FunctionInfo("5.2.14", "Однооконное приложение с использованием WEB-технологий",
                 OperationType.USER_INTERFACE, 300, 12000, FunctionType.STRUCTURAL, "Пользовательский интерфейс"),

    # 5.3. Реализация машинной графики
    FunctionInfo("5.3.1", "Реализация машинной графики (статика)",
                 OperationType.USER_INTERFACE, 500, 1500, FunctionType.STRUCTURAL, "Машинная графика"),
    FunctionInfo("5.3.2", "Реализация машинной графики (динамика)",
                 OperationType.USER_INTERFACE, 500, 3000, FunctionType.STRUCTURAL, "Машинная графика"),
]


def get_function_by_id(function_id: str) -> Optional[FunctionInfo]:
    """Получить функцию по её идентификатору"""
    for func in FUNCTION_CATALOG:
        if func.id == function_id:
            return func
    return None


def get_functions_by_operation_type(op_type: OperationType) -> list[FunctionInfo]:
    """Получить все функции определённого типа операции"""
    return [f for f in FUNCTION_CATALOG if f.operation_type == op_type]


def get_functions_by_category(category: str) -> list[FunctionInfo]:
    """Получить все функции определённой категории"""
    return [f for f in FUNCTION_CATALOG if f.category == category]


def get_all_categories() -> list[str]:
    """Получить список всех категорий"""
    categories = set()
    for func in FUNCTION_CATALOG:
        if func.category:
            categories.add(func.category)
    return sorted(categories)


def search_functions(query: str) -> list[FunctionInfo]:
    """Поиск функций по названию"""
    query = query.lower()
    return [f for f in FUNCTION_CATALOG if query in f.name.lower() or query in f.id]
