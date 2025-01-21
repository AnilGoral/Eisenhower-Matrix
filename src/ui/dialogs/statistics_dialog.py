from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGridLayout, QWidget, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StatisticsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Statistics")
        self.resize(1000, 600)  # Increased initial size
        self.stats = parent.db.get_statistics()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Left side - Statistics with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setMinimumWidth(200)
        scroll.setMaximumWidth(250)
        
        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setSpacing(10)
        stats_layout.setContentsMargins(5, 5, 5, 5)

        # Overview section
        overview_frame = self.create_overview_frame()
        stats_layout.addWidget(overview_frame)

        # Per Quadrant sections
        for quadrant, data in self.stats['per_quadrant'].items():
            quad_frame = self.create_quadrant_frame(quadrant, data)
            stats_layout.addWidget(quad_frame)

        # Remove the stretch that was causing the empty space
        stats_layout.addWidget(QWidget(), 1)  # Small spacer instead of stretch
        
        scroll.setWidget(stats_container)
        main_layout.addWidget(scroll, stretch=35)

        # Right side - Pie Chart (65% of width)
        chart_container = QWidget()
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(10, 10, 10, 10)
        
        chart_title = QLabel("Current Task Distribution")
        chart_title.setStyleSheet("font-size: 14px; font-weight: bold; color: white; padding: 5px;")
        chart_title.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(chart_title)

        figure = Figure(facecolor='#323232')
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        ax = figure.add_subplot(111)
        
        # Prepare pie chart data
        labels = []
        sizes = []
        colors = ['#3498db', '#e74c3c', '#f1c40f', '#2ecc71']
        
        for quadrant, data in self.stats['per_quadrant'].items():
            if data['active_tasks'] > 0:
                labels.append(quadrant)
                sizes.append(data['active_tasks'])

        if sizes:
            wedges, texts, autotexts = ax.pie(sizes, 
                                            labels=labels,
                                            colors=colors,
                                            autopct='%1.1f%%',
                                            startangle=45,
                                            labeldistance=1.1,
                                            pctdistance=0.75)
            
            # Style the labels and percentages
            plt.setp(autotexts, color='white', size=9)  # Reduced font size
            plt.setp(texts, color='white', size=9)      # Reduced font size
            
        else:
            ax.text(0.5, 0.5, 'No active tasks', 
                   horizontalalignment='center',
                   verticalalignment='center',
                   color='white',
                   fontsize=12)
            ax.axis('off')
        
        chart_layout.addWidget(canvas)
        main_layout.addWidget(chart_container, stretch=65)

        self.setStyleSheet("""
            QDialog {
                background-color: #323232;
            }
            QFrame {
                background-color: #424242;
                border-radius: 5px;
                padding: 8px;
                margin: 0px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #424242;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #626262;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QLabel {
                padding: 1px;
                margin: 0px;
            }
        """)

    def wrap_label(self, text, width=20):
        """Wrap long labels to multiple lines"""
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
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        layout = QGridLayout(frame)
        layout.setSpacing(5)  # Reduced spacing
        layout.setContentsMargins(8, 8, 8, 8)  # Reduced margins
        
        title = QLabel("Overview")
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        layout.addWidget(title, 0, 0, 1, 2)

        overview = self.stats['overview']
        labels = [
            ("Total Tasks Created:", overview['total_created']),
            ("Total Tasks Completed:", overview['total_completed']),
            ("Current Active Tasks:", overview['current_active']),
        ]
        
        for i, (label, value) in enumerate(labels, 1):
            label_widget = QLabel(label)
            value_widget = QLabel(str(value))
            label_widget.setStyleSheet("color: white; font-size: 12px;")
            value_widget.setStyleSheet("color: white; font-size: 12px;")
            layout.addWidget(label_widget, i, 0)
            layout.addWidget(value_widget, i, 1)
            
        return frame

    def create_quadrant_frame(self, quadrant, data):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        layout = QGridLayout(frame)
        layout.setSpacing(5)  # Reduced spacing
        layout.setContentsMargins(8, 8, 8, 8)  # Reduced margins
        
        title = QLabel(quadrant)
        title.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        layout.addWidget(title, 0, 0, 1, 2)

        avg_time = data['avg_completion_time']
        if avg_time:
            hours = int(avg_time // 60)
            minutes = int(avg_time % 60)
            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        else:
            time_str = "N/A"

        stats = [
            ("Tasks Created:", data['total_created']),
            ("Tasks Completed:", data['completed']),
            ("Active Tasks:", data['active_tasks']),
            ("Average Completion Time:", time_str),
            ("Completion Rate:", f"{data['completion_rate']:.1f}%"),
        ]
        
        for i, (label, value) in enumerate(stats, 1):
            label_widget = QLabel(label)
            value_widget = QLabel(str(value))
            label_widget.setStyleSheet("color: white; font-size: 12px;")
            value_widget.setStyleSheet("color: white; font-size: 12px;")
            layout.addWidget(label_widget, i, 0)
            layout.addWidget(value_widget, i, 1)
            
        return frame 