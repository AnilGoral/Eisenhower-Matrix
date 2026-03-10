import uuid
import os
from typing import Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QGridLayout, QSystemTrayIcon,
                            QMenu, QDialog, QLabel, QFileDialog, QMessageBox,
                            QApplication, QHBoxLayout, QVBoxLayout, QPushButton,
                            QShortcut, QLineEdit, QSizeGrip)
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QIcon, QColor, QKeySequence, QFont

from src.ui.theme import Theme

from src.utils.constants import WINDOW_TITLE, QUADRANT_NAMES, QUADRANT_ACCENTS, QUADRANT_BG_TINTS
from src.database.db_manager import DatabaseManager
from src.ui.widgets.quadrant_widget import QuadrantWidget
from src.utils.data_manager import DataManager
from src.utils.settings_manager import SettingsManager
from src.utils.undo_manager import UndoManager, Action, ActionType




class TitleBar(QWidget):
    """Custom title bar with close, minimize, and settings buttons."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(round(44 * Theme._scale))
        self.setObjectName("titleBar")
        self.dragging = False
        self.offset = QPoint()
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 8, 0)
        layout.setSpacing(0)

        # App icon dot
        dot = QLabel("●")
        dot.setStyleSheet(f"color: #4ECDC4; font-size: {Theme.px(Theme.FONT_DOT_LG)}px; background: transparent; margin-right: 6px;")
        layout.addWidget(dot)

        # App title
        title = QLabel(WINDOW_TITLE)
        title.setObjectName("titleLabel")
        title.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.Bold))
        layout.addWidget(title)

        layout.addStretch()

        # Window control buttons
        for icon_text, tooltip, callback, obj_name in [
            ("⚙", "Settings (Ctrl+S)", self.parent_window.show_settings, "settingsBtn"),
            ("─", "Minimize", self.parent_window.showMinimized, "minimizeBtn"),
            ("✕", "Close", self.parent_window.close, "closeBtn"),
        ]:
            btn = QPushButton(icon_text)
            btn.setToolTip(tooltip)
            btn.setObjectName(obj_name)
            btn_size = round(38 * Theme._scale)
            btn.setFixedSize(btn_size, btn_size)
            btn.setFont(Theme.font("Segoe UI", Theme.PT_CAPTION))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

    # --- Drag support ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.parent_window.move(event.globalPos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False


class EisenhowerMatrixApp(QMainWindow):
    def __init__(self, app_data_dir: Optional[str] = None,
                 resource_base: Optional[str] = None):
        super().__init__()
        self.app_data_dir = app_data_dir or os.path.join(os.path.expanduser('~'), '.eisenhower_matrix')
        self.resource_base = resource_base or os.path.abspath(os.path.dirname(__file__))

        # Settings manager
        self.settings_mgr = SettingsManager(self.app_data_dir)

        # Appearance from settings
        appearance = self.settings_mgr.settings.get('appearance', {})
        self.current_bg_color = QColor(appearance.get('background_color', '#0f0f1a'))
        self.current_text_color = QColor(appearance.get('text_color', '#E8E8F0'))
        self.current_opacity = appearance.get('opacity', 97)

        # Font scale
        font_scale = appearance.get('font_scale', 100)
        Theme.set_scale(font_scale)

        # Quadrant names from settings
        self.quadrant_names = self.settings_mgr.settings.get('quadrants', {}).get('names', list(QUADRANT_NAMES))

        self.setup_window()
        self.setup_database()
        self.undo_mgr = UndoManager()
        self.setup_ui()
        self.setup_tray()
        self.setup_shortcuts()
        self.load_tasks()
        self.data_manager = DataManager(self.db, self.app_data_dir)

    # ------------------------------------------------------------------ setup
    def setup_window(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set window icon for taskbar
        icon_path = os.path.join(self.resource_base, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        win = self.settings_mgr.settings.get('window', {})
        self.setGeometry(
            win.get('x', 100), win.get('y', 100),
            win.get('width', 750), win.get('height', 580)
        )
        self.setMinimumSize(550, 420)

    def setup_database(self):
        db_path = os.path.join(self.app_data_dir, 'tasks.db')
        self.db = DatabaseManager(db_path)

    def setup_ui(self):
        # Root container
        root = QWidget()
        root.setObjectName("rootContainer")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Custom title bar
        self.title_bar = TitleBar(self)
        root_layout.addWidget(self.title_bar)

        # Quadrant grid
        grid_container = QWidget()
        grid_container.setObjectName("gridContainer")
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(12, 6, 12, 10)

        self.quadrants = {}
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for idx, (name, pos) in enumerate(zip(self.quadrant_names, positions)):
            quadrant = QuadrantWidget(
                name,
                self.add_task,
                self.update_task_status,
                self.delete_task,
                self.edit_task,
                self.move_task,
                on_task_due_date_change=self.update_task_due_date,
                on_task_notes_change=self.update_task_notes,
                accent_color=QUADRANT_ACCENTS.get(idx, "#888888"),
                bg_tint=QUADRANT_BG_TINTS.get(idx, "rgba(255,255,255,0.04)")
            )
            grid_layout.addWidget(quadrant, *pos)
            self.quadrants[name] = quadrant

        root_layout.addWidget(grid_container, stretch=1)

        # Resize grip
        grip_container = QWidget()
        grip_container.setObjectName("gripContainer")
        grip_container.setFixedHeight(14)
        grip_layout = QHBoxLayout(grip_container)
        grip_layout.setContentsMargins(0, 0, 6, 2)
        grip_layout.addStretch()
        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(14, 14)
        self.size_grip.setStyleSheet("background: transparent;")
        grip_layout.addWidget(self.size_grip)
        root_layout.addWidget(grip_container)

        # Apply stylesheet
        self._apply_full_style()

    def setup_tray(self):
        icon_path = os.path.join(self.resource_base, "icon.png")
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))

        tray_menu = QMenu()
        tray_menu.addAction("Show/Hide", self.toggle_visibility)
        tray_menu.addAction("Statistics", self.show_statistics)
        tray_menu.addAction("Settings", self.show_settings)
        tray_menu.addSeparator()
        tray_menu.addAction("Quit", self.quit_application)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+N"), self, self._shortcut_new_task)
        QShortcut(QKeySequence("Ctrl+S"), self, self.show_settings)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.quit_application)
        QShortcut(QKeySequence("Ctrl+T"), self, self.show_statistics)
        QShortcut(QKeySequence("Ctrl+Z"), self, self._undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self._redo)

    # ---------------------------------------------------------- task actions
    def add_task(self, quadrant_name: str, description: str):
        task_id = str(uuid.uuid4())
        if self.db.add_task(task_id, quadrant_name, description):
            self.quadrants[quadrant_name].add_task_widget(task_id, description, False)
            self.undo_mgr.record(Action(
                ActionType.ADD_TASK, task_id,
                {'quadrant': quadrant_name, 'description': description},
                f'Add "{description[:30]}"'
            ))

    def update_task_status(self, task_id: str, done: bool):
        try:
            self.db.update_task_status(task_id, done)
            self.undo_mgr.record(Action(
                ActionType.STATUS_CHANGE, task_id,
                {'done': done, 'prev_done': not done},
                f'{"Complete" if done else "Reopen"} task'
            ))
        except Exception as e:
            print(f"Error updating task status: {e}")

    def delete_task(self, task_id: str):
        # Save task data for undo before deleting
        task_data = self.db.get_task_by_id(task_id)
        if self.db.delete_task(task_id):
            for quadrant in self.quadrants.values():
                for i in range(quadrant.task_layout.count()):
                    item = quadrant.task_layout.itemAt(i)
                    widget = item.widget() if item else None
                    if widget and hasattr(widget, 'task_id') and widget.task_id == task_id:
                        widget.setParent(None)
                        widget.deleteLater()
                        if task_data:
                            self.undo_mgr.record(Action(
                                ActionType.DELETE_TASK, task_id,
                                task_data,
                                f'Delete "{task_data.get("description", "")[:30]}"'
                            ))
                        return

    def edit_task(self, task_id: str, new_description: str):
        try:
            task_data = self.db.get_task_by_id(task_id)
            old_desc = task_data['description'] if task_data else ''
            self.db.update_task_description(task_id, new_description)
            self.undo_mgr.record(Action(
                ActionType.EDIT_TASK, task_id,
                {'new_description': new_description, 'old_description': old_desc},
                f'Edit task'
            ))
        except Exception as e:
            print(f"Error updating task: {e}")

    def move_task(self, task_id: str, source_quadrant: str, target_quadrant: str, target_index: int):
        try:
            self.db.move_task(task_id, target_quadrant)
            source = self.quadrants[source_quadrant]
            target = self.quadrants[target_quadrant]

            task_widget = None
            for i in range(source.task_layout.count() - 1):
                widget = source.task_layout.itemAt(i).widget()
                if widget and hasattr(widget, 'task_id') and widget.task_id == task_id:
                    task_widget = widget
                    source.task_layout.removeWidget(widget)
                    break

            if task_widget:
                task_widget.quadrant_name = target_quadrant
                target.task_layout.insertWidget(target_index, task_widget)
                source._update_task_count()
                target._update_task_count()
                self.undo_mgr.record(Action(
                    ActionType.MOVE_TASK, task_id,
                    {'source': source_quadrant, 'target': target_quadrant},
                    f'Move task to {target_quadrant}'
                ))
        except Exception as e:
            print(f"Error moving task: {e}")

    def update_task_due_date(self, task_id: str, due_date: str, old_date: str = ""):
        try:
            self.db.update_task_due_date(task_id, due_date)
            self.undo_mgr.record(Action(
                ActionType.DUE_DATE_CHANGE, task_id,
                {'new_date': due_date, 'old_date': old_date},
                f'Set due date'
            ))
        except Exception as e:
            print(f"Error updating due date: {e}")

    def update_task_notes(self, task_id: str, notes: str):
        try:
            self.db.update_task_notes(task_id, notes)
        except Exception as e:
            print(f"Error updating notes: {e}")

    def load_tasks(self):
        for quadrant_name, quadrant in self.quadrants.items():
            while quadrant.task_layout.count() > 1:
                item = quadrant.task_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
            for task_id, description, done, due_date, notes in self.db.get_tasks(quadrant_name):
                quadrant.add_task_widget(task_id, description, bool(done),
                                       due_date=due_date or '', notes=notes or '')

    # -------------------------------------------------------------- shortcuts
    def _shortcut_new_task(self):
        if self.quadrant_names:
            self.quadrants[self.quadrant_names[0]]._show_task_input()

    # ---------------------------------------------------------- undo / redo
    def _undo(self):
        action = self.undo_mgr.undo()
        if not action:
            return
        self._execute_undo(action)
        self._show_toast(f"Undid: {action.description}")

    def _redo(self):
        action = self.undo_mgr.redo()
        if not action:
            return
        self._execute_redo(action)
        self._show_toast(f"Redid: {action.description}")

    def _execute_undo(self, action: Action):
        """Reverse an action."""
        if action.action_type == ActionType.ADD_TASK:
            # Undo add = delete the task
            self.db.delete_task(action.task_id)
            self._remove_task_widget(action.task_id)
        elif action.action_type == ActionType.DELETE_TASK:
            # Undo delete = re-add the task
            d = action.data
            self.db.add_task(d['id'], d['quadrant'], d['description'], d['done'])
            if d.get('due_date'):
                self.db.update_task_due_date(d['id'], d['due_date'])
            if d.get('notes'):
                self.db.update_task_notes(d['id'], d['notes'])
            q = d['quadrant']
            if q in self.quadrants:
                self.quadrants[q].add_task_widget(
                    d['id'], d['description'], d['done'],
                    due_date=d.get('due_date', ''), notes=d.get('notes', '')
                )
        elif action.action_type == ActionType.EDIT_TASK:
            old_desc = action.data.get('old_description', '')
            self.db.update_task_description(action.task_id, old_desc)
            self._update_task_label(action.task_id, old_desc)
        elif action.action_type == ActionType.STATUS_CHANGE:
            prev_done = action.data.get('prev_done', False)
            self.db.update_task_status(action.task_id, prev_done)
            self._update_task_done_style(action.task_id, prev_done)
        elif action.action_type == ActionType.MOVE_TASK:
            src = action.data.get('target')  # reverse
            tgt = action.data.get('source')
            self.db.move_task(action.task_id, tgt)
            self._move_task_widget(action.task_id, src, tgt)
        elif action.action_type == ActionType.DUE_DATE_CHANGE:
            old_date = action.data.get('old_date', '')
            self.db.update_task_due_date(action.task_id, old_date)
            self._update_task_due_label(action.task_id, old_date)

    def _execute_redo(self, action: Action):
        """Re-apply an undone action."""
        if action.action_type == ActionType.ADD_TASK:
            d = action.data
            self.db.add_task(action.task_id, d['quadrant'], d['description'])
            q = d['quadrant']
            if q in self.quadrants:
                self.quadrants[q].add_task_widget(action.task_id, d['description'], False)
        elif action.action_type == ActionType.DELETE_TASK:
            self.db.delete_task(action.task_id)
            self._remove_task_widget(action.task_id)
        elif action.action_type == ActionType.EDIT_TASK:
            new_desc = action.data.get('new_description', '')
            self.db.update_task_description(action.task_id, new_desc)
            self._update_task_label(action.task_id, new_desc)
        elif action.action_type == ActionType.STATUS_CHANGE:
            done = action.data.get('done', False)
            self.db.update_task_status(action.task_id, done)
            self._update_task_done_style(action.task_id, done)
        elif action.action_type == ActionType.MOVE_TASK:
            src = action.data.get('source')
            tgt = action.data.get('target')
            self.db.move_task(action.task_id, tgt)
            self._move_task_widget(action.task_id, src, tgt)
        elif action.action_type == ActionType.DUE_DATE_CHANGE:
            new_date = action.data.get('new_date', '')
            self.db.update_task_due_date(action.task_id, new_date)
            self._update_task_due_label(action.task_id, new_date)

    # ---- Helper methods for undo/redo ----
    def _find_task_widget(self, task_id: str):
        for quadrant in self.quadrants.values():
            for i in range(quadrant.task_layout.count()):
                w = quadrant.task_layout.itemAt(i).widget()
                if w and hasattr(w, 'task_id') and w.task_id == task_id:
                    return w, quadrant
        return None, None

    def _remove_task_widget(self, task_id: str):
        w, q = self._find_task_widget(task_id)
        if w:
            w.setParent(None)
            w.deleteLater()
            QTimer.singleShot(0, q._update_task_count)

    def _update_task_label(self, task_id: str, text: str):
        w, _ = self._find_task_widget(task_id)
        if w:
            w.description = text
            w.task_label.setText(text)

    def _update_task_done_style(self, task_id: str, done: bool):
        w, _ = self._find_task_widget(task_id)
        if w:
            w.done_checkbox.blockSignals(True)
            w.done_checkbox.setChecked(done)
            w.done_checkbox.blockSignals(False)
            w._apply_done_style(done)

    def _update_task_due_label(self, task_id: str, due_date: str):
        w, _ = self._find_task_widget(task_id)
        if w:
            w.due_date = due_date
            w._update_due_label()

    def _move_task_widget(self, task_id: str, source_name: str, target_name: str):
        w, src_q = self._find_task_widget(task_id)
        if w and source_name in self.quadrants and target_name in self.quadrants:
            src_q.task_layout.removeWidget(w)
            tgt_q = self.quadrants[target_name]
            w.quadrant_name = target_name
            tgt_q.task_layout.insertWidget(tgt_q.task_layout.count() - 1, w)
            src_q._update_task_count()
            tgt_q._update_task_count()

    def _show_toast(self, message: str):
        """Show a brief toast message at the bottom of the window."""
        toast = QLabel(message, self)
        toast.setAlignment(Qt.AlignCenter)
        toast.setStyleSheet(f"""
            QLabel {{
                background: rgba(30, 30, 50, 0.92);
                color: #E8E8F0;
                font-size: {Theme.px(Theme.FONT_CAPTION)}px;
                font-family: "Segoe UI";
                border-radius: 8px;
                padding: 8px 18px;
                border: 1px solid rgba(255,255,255,0.1);
            }}
        """)
        toast.adjustSize()
        toast.move(
            (self.width() - toast.width()) // 2,
            self.height() - toast.height() - 30
        )
        toast.show()
        QTimer.singleShot(2000, toast.deleteLater)

    # --------------------------------------------------- window events
    def closeEvent(self, event):
        self._save_geometry()
        event.ignore()
        self.hide()

    def show(self):
        self.showNormal()
        self.activateWindow()

    def hide(self):
        super().hide()

    # --------------------------------------------------- settings / dialogs
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
            self.current_bg_color = dialog.appearance_tab.current_bg_color
            self.current_text_color = dialog.appearance_tab.current_text_color
            self.current_opacity = dialog.appearance_tab.opacity_spin.value()

            # Batch all settings writes (auto_save=False), then save once
            self.settings_mgr.set('appearance', 'background_color', self.current_bg_color.name(), auto_save=False)
            self.settings_mgr.set('appearance', 'text_color', self.current_text_color.name(), auto_save=False)
            self.settings_mgr.set('appearance', 'opacity', self.current_opacity, auto_save=False)

            # Font scale
            old_scale = Theme.get_scale()
            font_scale = dialog.appearance_tab.font_scale_slider.value()
            self.settings_mgr.set('appearance', 'font_scale', font_scale, auto_save=False)
            Theme.set_scale(font_scale)
            font_scale_changed = (old_scale != font_scale)

            new_names = dialog.quadrants_tab.get_quadrant_names()
            if new_names != self.quadrant_names:
                self.quadrant_names = new_names
                self.update_quadrant_names()
                self.settings_mgr.set('quadrants', 'names', self.quadrant_names, auto_save=False)

            # Single disk write for all settings
            self.settings_mgr.save_settings()

            self._apply_full_style()

            # Only rebuild UI if font scale actually changed
            if font_scale_changed:
                self._rebuild_quadrant_headers()
                self.load_tasks()

    def update_quadrant_names(self):
        for quadrant, name in zip(self.quadrants.values(), self.quadrant_names):
            title_label = quadrant.findChild(QLabel, "quadrantTitle")
            if title_label:
                title_label.setText(name)

    def _rebuild_quadrant_headers(self):
        """Re-apply Theme-scaled fonts to all quadrant header elements."""
        for quadrant in self.quadrants.values():
            # Title label
            title = quadrant.findChild(QLabel, "quadrantTitle")
            if title:
                title.setFont(Theme.font("Segoe UI", Theme.PT_HEADLINE, QFont.DemiBold))
                color = quadrant.accent_color
                title.setStyleSheet(f"""
                    color: {color};
                    font-size: {Theme.px(Theme.FONT_HEADLINE)}px;
                    font-weight: 600;
                    background: transparent;
                    letter-spacing: 0.3px;
                """)
            # Task count badge
            if hasattr(quadrant, 'task_count_label'):
                quadrant.task_count_label.setStyleSheet(f"""
                    color: rgba(255,255,255,0.3);
                    font-size: {Theme.px(Theme.FONT_TITLE)}px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 10px;
                    padding: 2px 8px;
                """)
            # Title bar dot and add button use global styles, so _apply_full_style covers them

    def show_statistics(self):
        from .dialogs.statistics_dialog import StatisticsDialog
        dialog = StatisticsDialog(self)
        dialog.exec_()

    # ------------------------------------------------------- import / export
    def export_to_json(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Tasks", "", "JSON Files (*.json)")
        if filepath:
            try:
                saved_path = self.data_manager.export_to_json(filepath)
                QMessageBox.information(self, "Success", f"Tasks exported to:\n{saved_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def export_to_csv(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Tasks", "", "CSV Files (*.csv)")
        if filepath:
            try:
                saved_path = self.data_manager.export_to_csv(filepath)
                QMessageBox.information(self, "Success", f"Tasks exported to:\n{saved_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def import_from_json(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Tasks", "", "JSON Files (*.json)")
        if filepath:
            success, message = self.data_manager.import_from_json(filepath)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_tasks()
            else:
                QMessageBox.critical(self, "Error", message)

    def import_from_csv(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Tasks", "", "CSV Files (*.csv)")
        if filepath:
            success, message = self.data_manager.import_from_csv(filepath)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_tasks()
            else:
                QMessageBox.critical(self, "Error", message)

    # --------------------------------------------------- quit / toggle
    def quit_application(self):
        self._save_geometry()
        self.db.conn.close()
        QApplication.quit()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    # --------------------------------------------------- helpers
    def _save_geometry(self):
        geo = self.geometry()
        self.settings_mgr.set('window', 'x', geo.x())
        self.settings_mgr.set('window', 'y', geo.y())
        self.settings_mgr.set('window', 'width', geo.width())
        self.settings_mgr.set('window', 'height', geo.height())

    def _apply_full_style(self):
        """Apply the premium master stylesheet."""
        opa = self.current_opacity / 100
        self.centralWidget().setStyleSheet(
            Theme.app_stylesheet(self.current_bg_color,
                                 self.current_text_color.name(), opa)
        )