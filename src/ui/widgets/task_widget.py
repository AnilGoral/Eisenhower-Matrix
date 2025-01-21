from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QCheckBox, 
                            QSizePolicy, QMenu, QLineEdit, QApplication, QPushButton)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QPainter
from src.utils.constants import TASK_LABEL_STYLE, TASK_MARGINS

class TaskWidget(QWidget):
    def __init__(self, task_id: str, description: str, done: bool, quadrant_name: str):
        super().__init__()
        self.task_id = task_id
        self.quadrant_name = quadrant_name
        self.description = description
        self.editing = False
        self.setup_ui(description, done)
        
        # Enable mouse tracking for drag and drop
        self.setMouseTracking(True)

    def setup_ui(self, description: str, done: bool):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(*TASK_MARGINS)
        self.layout.setSpacing(5)

        # Task Label
        self.task_label = QLabel(description)
        self.task_label.setWordWrap(True)
        self.task_label.setStyleSheet(TASK_LABEL_STYLE)
        self.task_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addWidget(self.task_label)

        # Edit Input (hidden by default)
        self.edit_input = QLineEdit(description)
        self.edit_input.setStyleSheet(TASK_LABEL_STYLE)
        self.edit_input.hide()
        self.edit_input.returnPressed.connect(self.finish_editing)
        self.edit_input.focusOutEvent = lambda e: self.finish_editing()
        self.layout.addWidget(self.edit_input)

        # Done Checkbox
        self.done_checkbox = QCheckBox()
        self.done_checkbox.setChecked(done)
        self.done_checkbox.stateChanged.connect(self.on_status_change)
        self.layout.addWidget(self.done_checkbox, alignment=Qt.AlignRight)

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)


    def show_context_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction("Edit Task")
        delete_action = menu.addAction("Delete Task")
        
        action = menu.exec_(self.mapToGlobal(position))
        if action == delete_action:
            self.on_delete(self.task_id)
        elif action == edit_action:
            self.start_editing()

    def start_editing(self):
        self.editing = True
        self.task_label.hide()
        self.edit_input.show()
        self.edit_input.setFocus()
        self.edit_input.selectAll()

    def finish_editing(self):
        if self.editing:
            self.editing = False
            new_text = self.edit_input.text().strip()
            if new_text and new_text != self.description:
                self.description = new_text
                self.task_label.setText(new_text)
                if hasattr(self, 'on_edit'):
                    self.on_edit(self.task_id, new_text)
            
            self.edit_input.hide()
            self.task_label.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if not hasattr(self, 'drag_start_position'):
            return
        
        # Check if the mouse has moved far enough to start a drag
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        # Store both task ID and current quadrant name
        mime_data.setText(f"{self.task_id}|{self.quadrant_name}")
        drag.setMimeData(mime_data)

        # Create a pixmap of the task description for visual feedback
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        # Start the drag operation
        drag.exec_(Qt.MoveAction)

    def on_status_change(self, state):
        """Handle checkbox state changes"""
        done = bool(state == Qt.Checked)
        if hasattr(self, 'on_task_status_change'):
            self.on_task_status_change(self.task_id, done)
