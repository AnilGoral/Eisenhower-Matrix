from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QFrame, QGridLayout, QWidget, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.ui.theme import Theme
from src.utils.constants import QUADRANT_NAMES, QUADRANT_ACCENTS

# Build name→color mapping from shared constants
QUADRANT_COLORS = {name: QUADRANT_ACCENTS[i] for i, name in enumerate(QUADRANT_NAMES)}


class StatisticsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Statistics")
        self.resize(900, 550)
        self.stats = parent.db.get_statistics()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Left side — Stats cards with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setMinimumWidth(220)
        scroll.setMaximumWidth(260)

        stats_container = QWidget()
        stats_container.setStyleSheet("background: transparent;")
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setSpacing(8)
        stats_layout.setContentsMargins(4, 4, 4, 4)

        # Overview section
        overview_frame = self.create_overview_frame()
        stats_layout.addWidget(overview_frame)

        # Per-quadrant sections
        for quadrant, data in self.stats['per_quadrant'].items():
            quad_frame = self.create_quadrant_frame(quadrant, data)
            stats_layout.addWidget(quad_frame)

        stats_layout.addStretch()
        scroll.setWidget(stats_container)
        main_layout.addWidget(scroll, stretch=35)

        # Right side — Pie Chart
        chart_container = QWidget()
        chart_container.setStyleSheet("background: transparent;")
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(8, 8, 8, 8)

        chart_title = QLabel("Task Distribution")
        chart_title.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.Bold))
        chart_title.setStyleSheet(f"font-size: {Theme.px(Theme.FONT_TITLE)}px; font-weight: bold; color: #E8E8F0; padding: 4px;")
        chart_title.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(chart_title)

        bg_color = '#1e1e32'
        figure = Figure(facecolor=bg_color)
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        ax = figure.add_subplot(111)
        ax.set_facecolor(bg_color)

        # Prepare pie chart data
        labels = []
        sizes = []
        colors = []

        for quadrant, data in self.stats['per_quadrant'].items():
            if data['active_tasks'] > 0:
                labels.append(self._wrap_label(quadrant, 18))
                sizes.append(data['active_tasks'])
                colors.append(QUADRANT_COLORS.get(quadrant, '#888888'))

        if sizes:
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct='%1.0f%%',
                startangle=90,
                labeldistance=1.15,
                pctdistance=0.75,
                wedgeprops={'linewidth': 2, 'edgecolor': bg_color},
            )
            plt.setp(autotexts, color='white', size=Theme.pt(13), fontweight='bold')
            plt.setp(texts, color='#B8B8C8', size=Theme.pt(12))
        else:
            ax.text(0.5, 0.5, 'No active tasks',
                   horizontalalignment='center',
                   verticalalignment='center',
                   color='#666680',
                   fontsize=Theme.pt(Theme.PT_TITLE),
                   transform=ax.transAxes)
            ax.axis('off')

        chart_layout.addWidget(canvas)
        main_layout.addWidget(chart_container, stretch=65)

        self.setStyleSheet(Theme.stats_stylesheet())

    def _wrap_label(self, text, width=20):
        """Wrap long labels to multiple lines."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word) + 1

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)

    def create_overview_frame(self):
        frame = QFrame()
        layout = QGridLayout(frame)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("📊  Overview")
        title.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.Bold))
        title.setStyleSheet(f"font-size: {Theme.px(Theme.FONT_BODY)}px; font-weight: bold; color: #E8E8F0;")
        layout.addWidget(title, 0, 0, 1, 2)

        overview = self.stats['overview']
        labels = [
            ("Total Created:", overview['total_created']),
            ("Completed:", overview['total_completed']),
            ("Active:", overview['current_active']),
        ]

        for i, (label, value) in enumerate(labels, 1):
            label_widget = QLabel(label)
            value_widget = QLabel(str(value))
            label_widget.setStyleSheet(f"color: rgba(255,255,255,0.6); font-size: {Theme.px(Theme.FONT_BODY_SM)}px;")
            value_widget.setStyleSheet(f"color: #E8E8F0; font-size: {Theme.px(Theme.FONT_BODY_SM)}px; font-weight: bold;")
            value_widget.setAlignment(Qt.AlignRight)
            layout.addWidget(label_widget, i, 0)
            layout.addWidget(value_widget, i, 1)

        return frame

    def create_quadrant_frame(self, quadrant, data):
        frame = QFrame()
        accent = QUADRANT_COLORS.get(quadrant, '#888888')
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #252540;
                border-radius: 8px;
                border-left: 3px solid {accent};
                border-top: none;
                border-right: 1px solid rgba(255,255,255,0.06);
                border-bottom: 1px solid rgba(255,255,255,0.06);
                padding: 10px;
            }}
        """)
        layout = QGridLayout(frame)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 8, 10, 8)

        title = QLabel(quadrant)
        title.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.Bold))
        title.setStyleSheet(f"font-size: {Theme.px(Theme.FONT_BODY_SM)}px; font-weight: bold; color: {accent};")
        layout.addWidget(title, 0, 0, 1, 2)

        avg_time = data['avg_completion_time']
        if avg_time:
            hours = int(avg_time // 60)
            minutes = int(avg_time % 60)
            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        else:
            time_str = "—"

        stats = [
            ("Created:", data['total_created']),
            ("Done:", data['completed']),
            ("Active:", data['active_tasks']),
            ("Avg Time:", time_str),
            ("Rate:", f"{data['completion_rate']:.0f}%"),
        ]

        for i, (label, value) in enumerate(stats, 1):
            label_widget = QLabel(label)
            value_widget = QLabel(str(value))
            label_widget.setStyleSheet(f"color: rgba(255,255,255,0.5); font-size: {Theme.px(Theme.FONT_CAPTION)}px;")
            value_widget.setStyleSheet(f"color: #E8E8F0; font-size: {Theme.px(Theme.FONT_CAPTION)}px; font-weight: bold;")
            value_widget.setAlignment(Qt.AlignRight)
            layout.addWidget(label_widget, i, 0)
            layout.addWidget(value_widget, i, 1)

        return frame