# -*- coding: utf-8 -*-
"""
Виджет для отображения диаграмм
"""

from typing import Dict

from PySide6.QtWidgets import QWidget, QVBoxLayout

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartWidget(QWidget):
    """Виджет для отображения диаграмм matplotlib"""

    def __init__(self, chart_type: str = "pie", parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if MATPLOTLIB_AVAILABLE:
            # Шрифты и контраст для читаемости
            plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
            plt.rcParams['font.size'] = 10
            plt.rcParams['axes.titlesize'] = 12
            plt.rcParams['axes.labelsize'] = 11

            self.figure = Figure(figsize=(6, 5), dpi=110)
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
        else:
            from PySide6.QtWidgets import QLabel
            label = QLabel("Для отображения диаграмм установите matplotlib")
            label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(label)

    def clear(self):
        """Очистить диаграмму"""
        if MATPLOTLIB_AVAILABLE:
            self.figure.clear()
            self.canvas.draw()

    def update_pie_chart(self, data: Dict[str, float], title: str = ""):
        """Обновить круговую диаграмму (читаемые подписи и проценты)"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if data:
            labels = list(data.keys())
            values = list(data.values())

            # Цвета с хорошим контрастом
            colors = ['#1565C0', '#2E7D32', '#E65100', '#6A1B9A', '#00838F']

            wedges, texts, autotexts = ax.pie(
                values,
                labels=None,
                autopct='%1.1f%%',
                colors=colors[:len(values)],
                startangle=90,
                pctdistance=0.75,
                labeldistance=1.05,
            )

            # Крупные проценты на секторах
            for t in autotexts:
                t.set_fontsize(12)
                t.set_fontweight('bold')
                t.set_color('#212121')

            # Легенда справа — крупный шрифт, тёмный текст
            leg = ax.legend(
                wedges, labels,
                title="Подпроцессы",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=11,
                title_fontsize=12,
            )
            leg.get_frame().set_facecolor('#FAFAFA')
            leg.get_frame().set_edgecolor('#E0E0E0')
            for t in leg.get_texts():
                t.set_color('#212121')

            if title:
                ax.set_title(title, fontsize=13, fontweight='bold', color='#212121')

            ax.set_facecolor('#FFFFFF')
            self.figure.patch.set_facecolor('#FFFFFF')

        self.figure.tight_layout()
        self.canvas.draw()

    def update_bar_chart(self, data: Dict[str, float], title: str = ""):
        """Обновить столбчатую диаграмму"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if data:
            labels = list(data.keys())
            values = list(data.values())

            short_labels = [l[:15] + "…" if len(l) > 15 else l for l in labels]

            bars = ax.bar(range(len(values)), values, color='#1565C0')

            ax.set_xticks(range(len(values)))
            ax.set_xticklabels(short_labels, rotation=45, ha='right', fontsize=11, color='#212121')
            ax.set_ylabel('Объём (строк)', fontsize=11, color='#212121')
            ax.tick_params(colors='#212121')

            if title:
                ax.set_title(title, fontsize=13, fontweight='bold', color='#212121')

            for bar, value in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f'{value:.0f}',
                    ha='center', va='bottom',
                    fontsize=11,
                    fontweight='bold',
                    color='#212121',
                )

            ax.set_facecolor('#FFFFFF')
            self.figure.patch.set_facecolor('#FFFFFF')

        self.figure.tight_layout()
        self.canvas.draw()
