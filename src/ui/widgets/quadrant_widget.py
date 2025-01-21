from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, 
                            QLineEdit, QApplication, QColorDialog)
from PyQt5.QtCore import Qt
from src.utils.constants import QUADRANT_MARGINS, TASK_SPACING
from .task_widget import TaskWidget

class QuadrantWidget(QWidget):
    def __init__(self, name: str, on_add_task, on_task_status_change, 
                 on_task_delete, on_task_edit, on_task_move):
        super().__init__()
        self.name = name
        self.on_add_task = on_add_task
        self.on_task_status_change = on_task_status_change
        self.on_task_delete = on_task_delete
        self.on_task_edit = on_task_edit
        self.on_task_move = on_task_move
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        
        # Title
        title = QLabel(self.name)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Scrollable task area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setSpacing(2)
        self.task_layout.addStretch()
        self.scroll.setWidget(self.task_container)
        layout.addWidget(self.scroll)

        # Enable drops
        self.setAcceptDrops(True)
        self.task_container.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        task_data = event.mimeData().text().split('|')
        if len(task_data) == 2:
            task_id, source_quadrant = task_data
            
            # Get the target position
            drop_pos = event.pos()
            target_index = self.get_drop_index(drop_pos)
            
            # If it's the same quadrant, adjust the index
            if source_quadrant == self.name:
                # Find current index of the task
                current_index = -1
                for i in range(self.task_layout.count() - 1):
                    widget = self.task_layout.itemAt(i).widget()
                    if widget and widget.task_id == task_id:
                        current_index = i
                        break
                
                # Adjust target index if moving down
                if current_index != -1 and target_index > current_index:
                    target_index -= 1
            
            # Handle the move
            if source_quadrant != self.name:
                self.on_task_move(task_id, source_quadrant, self.name, target_index)
            else:
                self.reorder_task(task_id, target_index)
            
            event.acceptProposedAction()

    def get_drop_index(self, y_pos):
        # Convert position to task container coordinates
        container_pos = self.task_container.mapFrom(self, y_pos)
        
        # Get the number of tasks (excluding stretch)
        task_count = self.task_layout.count() - 1
        
        for i in range(task_count):
            widget = self.task_layout.itemAt(i).widget()
            if widget:
                widget_bottom = widget.y() + widget.height()
                if container_pos.y() < widget_bottom:
                    return i
        
        # If we're below all widgets, return the last position before stretch
        return task_count

    def reorder_task(self, task_id, new_index):
        # Find the task widget
        task_widget = None
        current_index = -1
        
        for i in range(self.task_layout.count() - 1):
            widget = self.task_layout.itemAt(i).widget()
            if widget and widget.task_id == task_id:
                task_widget = widget
                current_index = i
                break
        
        if task_widget and current_index != new_index:
            # Remove and reinsert the widget
            self.task_layout.removeWidget(task_widget)
            self.task_layout.insertWidget(new_index, task_widget)

    def mouseDoubleClickEvent(self, event):
        task_input = QLineEdit()
        task_input.setPlaceholderText("Enter task...")
        task_input.setFixedHeight(30)
        task_input.returnPressed.connect(
            lambda: self.handle_new_task(task_input)
        )
        self.task_layout.insertWidget(self.task_layout.count() - 1, task_input)
        task_input.setFocus()

    def handle_new_task(self, input_field):
        description = input_field.text().strip()
        if description:
            input_field.deleteLater()
            self.on_add_task(self.name, description)

    def add_task_widget(self, task_id: str, description: str, done: bool):
        task = TaskWidget(task_id, description, done, self.name)
        task.done_checkbox.stateChanged.connect(
            lambda state: self.on_task_status_change(task_id, state)
        )
        task.on_delete = self.on_task_delete
        task.on_edit = self.on_task_edit
        self.task_layout.insertWidget(self.task_layout.count() - 1, task)

    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setStyleSheet(f"background-color: {color.name()};")
           