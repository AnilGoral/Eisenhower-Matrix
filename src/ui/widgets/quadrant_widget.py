from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QScrollArea, QLineEdit, QPushButton, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.utils.constants import TASK_SPACING
from src.ui.theme import Theme
from .task_widget import TaskWidget


class QuadrantWidget(QWidget):
    def __init__(self, name: str, on_add_task, on_task_status_change,
                 on_task_delete, on_task_edit, on_task_move,
                 on_task_due_date_change=None, on_task_notes_change=None,
                 accent_color: str = "#888888",
                 bg_tint: str = "rgba(255,255,255,0.04)"):
        super().__init__()
        self.name = name
        self.on_add_task = on_add_task
        self.on_task_status_change = on_task_status_change
        self.on_task_delete = on_task_delete
        self.on_task_edit = on_task_edit
        self.on_task_move = on_task_move
        self.on_task_due_date_change = on_task_due_date_change
        self.on_task_notes_change = on_task_notes_change
        self.accent_color = accent_color
        self.bg_tint = bg_tint
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Glass-card quadrant styling
        self.setStyleSheet(f"""
            QuadrantWidget {{
                background: {self.bg_tint};
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.06);
            }}
        """)

        # Header: colored accent bar + title + add button
        header = QWidget()
        header.setObjectName("quadrantHeader")
        header.setFixedHeight(42)
        header.setStyleSheet(f"""
            #quadrantHeader {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba({self._hex_to_rgba(self.accent_color, 0.15)}),
                    stop:1 rgba({self._hex_to_rgba(self.accent_color, 0.03)})
                );
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid rgba({self._hex_to_rgba(self.accent_color, 0.2)});
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 0, 8, 0)
        header_layout.setSpacing(6)

        # Accent dot
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {self.accent_color}; font-size: {Theme.px(Theme.FONT_MICRO)}px; background: transparent;")
        header_layout.addWidget(dot)

        # Title
        title = QLabel(self.name)
        title.setObjectName("quadrantTitle")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setFont(Theme.font("Segoe UI", Theme.PT_HEADLINE, QFont.DemiBold))
        title.setStyleSheet(f"""
            color: {self.accent_color};
            font-size: {Theme.px(Theme.FONT_HEADLINE)}px;
            font-weight: 600;
            background: transparent;
            letter-spacing: 0.3px;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Task counter
        self.task_count_label = QLabel("0")
        self.task_count_label.setStyleSheet(f"""
            color: rgba(255,255,255,0.3);
            font-size: {Theme.px(Theme.FONT_TITLE)}px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 2px 8px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.task_count_label)

        # "+" add button
        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.setToolTip("Add a new task")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: rgba(255, 255, 255, 0.35);
                border: 1.5px solid rgba(255, 255, 255, 0.1);
                border-radius: 14px;
                font-size: {Theme.px(Theme.FONT_TITLE)}px;
                font-weight: bold;
                padding-bottom: 2px;
            }}
            QPushButton:hover {{
                background: {self.accent_color};
                color: white;
                border-color: {self.accent_color};
            }}
        """)
        add_btn.clicked.connect(lambda: self._show_task_input())
        header_layout.addWidget(add_btn)

        layout.addWidget(header)

        # Scrollable task area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.task_container = QWidget()
        self.task_container.setStyleSheet("background: transparent;")
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setSpacing(TASK_SPACING)
        self.task_layout.setContentsMargins(8, 6, 8, 6)

        # Drop indicator line (hidden by default)
        self.drop_indicator = QFrame()
        self.drop_indicator.setFixedHeight(3)
        self.drop_indicator.setStyleSheet(f"""
            background: {self.accent_color};
            border-radius: 1px;
            margin: 0 12px;
        """)
        self.drop_indicator.hide()

        self.task_layout.addStretch()
        self.scroll.setWidget(self.task_container)
        layout.addWidget(self.scroll)

        # Enable drops
        self.setAcceptDrops(True)
        self.task_container.setAcceptDrops(True)

    def _hex_to_rgba(self, hex_color, alpha):
        """Convert hex color to r, g, b, alpha string for CSS."""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}, {alpha}"

    def _update_task_count(self):
        """Update the task counter badge."""
        count = 0
        for i in range(self.task_layout.count()):
            widget = self.task_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'task_id'):
                count += 1
        self.task_count_label.setText(str(count))

    # ---- Drag & Drop with visual feedback ----

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            # Highlight quadrant border
            self.setStyleSheet(f"""
                QuadrantWidget {{
                    background: {self.bg_tint};
                    border-radius: 12px;
                    border: 1px solid rgba({self._hex_to_rgba(self.accent_color, 0.4)});
                }}
            """)

    def dragLeaveEvent(self, event):
        # Remove highlight and hide drop indicator
        self.setStyleSheet(f"""
            QuadrantWidget {{
                background: {self.bg_tint};
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.06);
            }}
        """)
        self._hide_drop_indicator()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self._show_drop_indicator(event.pos())

    def _show_drop_indicator(self, pos):
        """Show a line indicating where the drop will occur."""
        container_pos = self.task_container.mapFrom(self, pos)
        task_count = self.task_layout.count() - 1  # minus stretch

        # Remove indicator from layout if already placed
        if self.drop_indicator.parent() == self.task_container:
            self.task_layout.removeWidget(self.drop_indicator)

        insert_index = task_count
        for i in range(task_count):
            widget = self.task_layout.itemAt(i).widget()
            if widget and widget != self.drop_indicator:
                widget_center = widget.y() + widget.height() // 2
                if container_pos.y() < widget_center:
                    insert_index = i
                    break

        self.task_layout.insertWidget(insert_index, self.drop_indicator)
        self.drop_indicator.show()

    def _hide_drop_indicator(self):
        """Hide the drop indicator line."""
        self.drop_indicator.hide()
        if self.drop_indicator.parent() == self.task_container:
            self.task_layout.removeWidget(self.drop_indicator)

    def dropEvent(self, event):
        # Remove highlight
        self.setStyleSheet(f"""
            QuadrantWidget {{
                background: {self.bg_tint};
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.06);
            }}
        """)
        self._hide_drop_indicator()

        task_data = event.mimeData().text().split('|')
        if len(task_data) == 2:
            task_id, source_quadrant = task_data
            drop_pos = event.pos()
            target_index = self.get_drop_index(drop_pos)

            if source_quadrant == self.name:
                current_index = -1
                for i in range(self.task_layout.count() - 1):
                    widget = self.task_layout.itemAt(i).widget()
                    if widget and hasattr(widget, 'task_id') and widget.task_id == task_id:
                        current_index = i
                        break
                if current_index != -1 and target_index > current_index:
                    target_index -= 1

            if source_quadrant != self.name:
                self.on_task_move(task_id, source_quadrant, self.name, target_index)
                self._update_task_count()
            else:
                self.reorder_task(task_id, target_index)

            event.acceptProposedAction()

    def get_drop_index(self, y_pos):
        container_pos = self.task_container.mapFrom(self, y_pos)
        task_count = self.task_layout.count() - 1
        for i in range(task_count):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget_bottom = widget.y() + widget.height()
                if container_pos.y() < widget_bottom:
                    return i
        return task_count

    def reorder_task(self, task_id, new_index):
        task_widget = None
        current_index = -1
        for i in range(self.task_layout.count() - 1):
            widget = self.task_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'task_id') and widget.task_id == task_id:
                task_widget = widget
                current_index = i
                break
        if task_widget and current_index != new_index:
            self.task_layout.removeWidget(task_widget)
            self.task_layout.insertWidget(new_index, task_widget)

    def mouseDoubleClickEvent(self, event):
        self._show_task_input()

    def _show_task_input(self):
        """Show an inline input field for adding a new task."""
        task_input = QLineEdit()
        task_input.setPlaceholderText("What needs to be done?")
        task_input.setFixedHeight(34)
        task_input.setFont(Theme.font("Segoe UI", Theme.PT_HEADLINE))
        task_input.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255, 255, 255, 0.06);
                border: 1.5px solid rgba({self._hex_to_rgba(self.accent_color, 0.4)});
                border-radius: 8px;
                color: #E8E8F0;
                padding: 5px 12px;
                font-size: {Theme.px(Theme.FONT_HEADLINE)}px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {self.accent_color};
                background: rgba(255, 255, 255, 0.08);
            }}
        """)
        task_input.returnPressed.connect(
            lambda: self.handle_new_task(task_input)
        )
        original_focus_out = task_input.focusOutEvent

        def on_focus_out(event):
            if task_input.text().strip():
                self.handle_new_task(task_input)
            else:
                task_input.deleteLater()
            original_focus_out(event)

        task_input.focusOutEvent = on_focus_out
        self.task_layout.insertWidget(self.task_layout.count() - 1, task_input)
        task_input.setFocus()

    def handle_new_task(self, input_field):
        description = input_field.text().strip()
        if description:
            input_field.deleteLater()
            self.on_add_task(self.name, description)

    def add_task_widget(self, task_id: str, description: str, done: bool,
                        due_date: str = "", notes: str = ""):
        task = TaskWidget(task_id, description, done, self.name, self.accent_color,
                         due_date=due_date, notes=notes)
        task.done_checkbox.stateChanged.connect(
            lambda state: self._handle_task_status(task, state == Qt.Checked)
        )
        task.on_delete = self._handle_task_delete
        task.on_edit = self.on_task_edit
        task.on_due_date_change = self.on_task_due_date_change
        task.on_notes_change = self.on_task_notes_change
        self.task_layout.insertWidget(self.task_layout.count() - 1, task)
        self._update_task_count()

    def _handle_task_delete(self, task_id: str):
        """Delete task and update count after widget is removed."""
        self.on_task_delete(task_id)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, self._update_task_count)

    def _handle_task_status(self, task_widget: TaskWidget, done: bool):
        """Handle checkbox toggle — update DB and apply visual feedback."""
        self.on_task_status_change(task_widget.task_id, done)
        task_widget._apply_done_style(done)