import sys
import uuid
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QSystemTrayIcon, 
                            QMenu, QDialog, QLabel, QFileDialog, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor

from src.utils.constants import WINDOW_TITLE, WINDOW_SIZE, WINDOW_POSITION, QUADRANT_NAMES, STYLE_SHEET
from src.database.db_manager import DatabaseManager
from src.ui.widgets.quadrant_widget import QuadrantWidget
from src.utils.data_manager import DataManager

class EisenhowerMatrixApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize with default colors
        self.current_bg_color = QColor("#646464")
        self.current_text_color = QColor("#FFFFFF")
        self.current_opacity = 95
        self.quadrant_names = [
            "Important & Urgent",
            "Important but Not Urgent",
            "Not Important but Urgent",
            "Not Important & Not Urgent"
        ]
        self.setup_window()
        self.setup_database()
        self.setup_ui()
        self.setup_tray()
        self.load_tasks()
        self.data_manager = DataManager(self.db)
        


    def setup_window(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(*WINDOW_POSITION, *WINDOW_SIZE)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.dragging = False

    def setup_database(self):
        self.db = DatabaseManager('tasks.db')

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Store the initial style sheet
        self.current_style = STYLE_SHEET
        central_widget.setStyleSheet(self.current_style)

        layout = QGridLayout(central_widget)
        self.quadrants = {}
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for name, pos in zip(self.quadrant_names, positions):
            quadrant = QuadrantWidget(
                name,
                self.add_task,
                self.update_task_status,
                self.delete_task,
                self.edit_task,
                self.move_task
            )
            layout.addWidget(quadrant, *pos)
            self.quadrants[name] = quadrant

    def setup_tray(self):
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide action
        toggle_action = tray_menu.addAction("Show/Hide")
        toggle_action.triggered.connect(self.toggle_visibility)
        
        # Statistics action
        stats_action = tray_menu.addAction("Statistics")
        stats_action.triggered.connect(self.show_statistics)
        
        # Settings action
        settings_action = tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings)
        
        tray_menu.addSeparator()
        
        # Quit action
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        # Set the tray menu
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def add_task(self, quadrant_name: str, description: str):
        task_id = str(uuid.uuid4())
        if self.db.add_task(task_id, quadrant_name, description):
            self.quadrants[quadrant_name].add_task_widget(task_id, description, False)

    def update_task_status(self, task_id: str, done: bool):
        """Update task status in database and UI"""
        try:
            # Update in database
            success = self.db.update_task_status(task_id, done)
            if not success:
                print(f"Failed to update task status: {task_id}")
            
            # Commit the changes to ensure they're saved
            self.db.conn.commit()
            
        except Exception as e:
            print(f"Error updating task status: {e}")

    def delete_task(self, task_id: str):
        if self.db.delete_task(task_id):
            # Task widget will be deleted through Qt's parent-child relationship
            sender = self.sender()
            if sender:
                sender.deleteLater()

    def load_tasks(self):
        for quadrant in QUADRANT_NAMES:
            for task_id, description, done in self.db.get_tasks(quadrant):
                self.quadrants[quadrant].add_task_widget(task_id, description, done)

    # Window drag events
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        
        # Stop notification manager
        self.notification_manager.stop()

    def show_settings(self):
        from .dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(
            parent=self,
            bg_color=self.current_bg_color,
            text_color=self.current_text_color,
            opacity=self.current_opacity,
            quadrant_names=self.quadrant_names
        )
        if dialog.exec_() == QDialog.Accepted:
            # Update the stored colors and apply new style
            self.current_bg_color = dialog.appearance_tab.current_bg_color
            self.current_text_color = dialog.appearance_tab.current_text_color
            self.current_opacity = dialog.appearance_tab.opacity_spin.value()
            
            # Update quadrant names
            new_names = dialog.quadrants_tab.get_quadrant_names()
            if new_names != self.quadrant_names:
                self.quadrant_names = new_names
                self.update_quadrant_names()
            
            self.apply_style()

    def update_quadrant_names(self):
        # Update the quadrant labels
        for quadrant, name in zip(self.quadrants.values(), self.quadrant_names):
            title_label = quadrant.findChild(QLabel)
            if title_label:
                title_label.setText(name)

    def apply_style(self):
        style_sheet = f"""
            QWidget {{
                background: rgba({self.current_bg_color.red()}, 
                               {self.current_bg_color.green()}, 
                               {self.current_bg_color.blue()}, 
                               {self.current_opacity/100});
                border-radius: 10px;
            }}
            QLabel {{
                color: {self.current_text_color.name()};
                font-size: 14px;
                font-weight: bold;
            }}
            QLineEdit {{
                font-size: 12px;
                color: {self.current_text_color.name()};
            }}
            QCheckBox {{
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 13px;
                height: 13px;
                background-color: white;
                border: 1px solid gray;
                border-radius: 2px;
            }}
            QCheckBox::indicator:checked {{
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
            }}
        """
        self.centralWidget().setStyleSheet(style_sheet)

    def show(self):
        self.showNormal()
        self.activateWindow()

    def hide(self):
        super().hide()

    def save_settings(self, bg_color, text_color, opacity):
        self.current_bg_color = bg_color
        self.current_text_color = text_color
        self.current_opacity = opacity 

    def edit_task(self, task_id: str, new_description: str):
        try:
            self.db.update_task_description(task_id, new_description)
        except Exception as e:
            print(f"Error updating task: {e}") 

    def move_task(self, task_id: str, source_quadrant: str, target_quadrant: str, target_index: int):
        try:
            # Update the database
            self.db.move_task(task_id, target_quadrant)
            
            # Update the UI
            # First, find and remove the task widget from the source quadrant
            source = self.quadrants[source_quadrant]
            target = self.quadrants[target_quadrant]
            
            task_widget = None
            for i in range(source.task_layout.count() - 1):
                widget = source.task_layout.itemAt(i).widget()
                if widget and widget.task_id == task_id:
                    task_widget = widget
                    source.task_layout.removeWidget(widget)
                    break
            
            if task_widget:
                # Update the task's quadrant name
                task_widget.quadrant_name = target_quadrant
                # Add it to the target quadrant at the specified index
                target.task_layout.insertWidget(target_index, task_widget)
                
        except Exception as e:
            print(f"Error moving task: {e}") 

    def export_to_json(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Tasks", "", "JSON Files (*.json)"
        )
        if filepath:
            try:
                saved_path = self.data_manager.export_to_json(filepath)
                QMessageBox.information(self, "Success", f"Tasks exported to:\n{saved_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export tasks: {str(e)}")

    def export_to_csv(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Tasks", "", "CSV Files (*.csv)"
        )
        if filepath:
            try:
                saved_path = self.data_manager.export_to_csv(filepath)
                QMessageBox.information(self, "Success", f"Tasks exported to:\n{saved_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export tasks: {str(e)}")

    def import_from_json(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Tasks", "", "JSON Files (*.json)"
        )
        if filepath:
            success, message = self.data_manager.import_from_json(filepath)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_tasks()  # Refresh the UI
            else:
                QMessageBox.critical(self, "Error", message)

    def import_from_csv(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Tasks", "", "CSV Files (*.csv)"
        )
        if filepath:
            success, message = self.data_manager.import_from_csv(filepath)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_tasks()  # Refresh the UI
            else:
                QMessageBox.critical(self, "Error", message)

    def quit_application(self):
        self.db.conn.close()  # Close database connection
        QApplication.quit()  # Quit the application 

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show() 

    def show_statistics(self):
        from .dialogs.statistics_dialog import StatisticsDialog
        dialog = StatisticsDialog(self)
        dialog.exec_() 