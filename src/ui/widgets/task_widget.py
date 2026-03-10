from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox,
                            QSizePolicy, QMenu, QLineEdit, QApplication,
                            QTextEdit, QDateEdit, QCalendarWidget, QPushButton)
from PyQt5.QtCore import Qt, QMimeData, QDate
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QFont, QColor
from src.utils.constants import TASK_MARGINS
from src.ui.theme import Theme


class TaskWidget(QWidget):
    def __init__(self, task_id: str, description: str, done: bool,
                 quadrant_name: str, accent_color: str = "#4ECDC4",
                 due_date: str = "", notes: str = ""):
        super().__init__()
        self.task_id = task_id
        self.quadrant_name = quadrant_name
        self.description = description
        self.accent_color = accent_color
        self.due_date = due_date or ""
        self.notes = notes or ""
        self.editing = False
        self.notes_visible = False
        self.on_delete = None
        self.on_edit = None
        self.on_due_date_change = None
        self.on_notes_change = None
        self.setup_ui(description, done)
        self.setMouseTracking(True)
        self.setCursor(Qt.OpenHandCursor)

    def setup_ui(self, description: str, done: bool):
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        # --- Top row: checkbox + label + due date ---
        top_row = QWidget()
        self.main_layout = QHBoxLayout(top_row)
        self.main_layout.setContentsMargins(10, 6, 10, 6)
        self.main_layout.setSpacing(8)

        # Checkbox
        self.done_checkbox = QCheckBox()
        self.done_checkbox.setChecked(done)
        self.done_checkbox.setFixedSize(28, 28)
        self.main_layout.addWidget(self.done_checkbox, alignment=Qt.AlignVCenter)

        # Task label
        self.task_label = QLabel(description)
        self.task_label.setWordWrap(True)
        self.task_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.task_label.setFont(Theme.font("Segoe UI", Theme.PT_HEADLINE))
        self.main_layout.addWidget(self.task_label)

        # Inline edit input (hidden by default)
        self.edit_input = QLineEdit(description)
        self.edit_input.hide()
        self.edit_input.returnPressed.connect(self.finish_editing)
        self.main_layout.addWidget(self.edit_input)

        # Due date label (right side)
        self.due_label = QLabel()
        self.due_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.due_label.setCursor(Qt.PointingHandCursor)
        self.due_label.setToolTip("Click to change due date")
        self._update_due_label()
        self.main_layout.addWidget(self.due_label, alignment=Qt.AlignVCenter)

        self.outer_layout.addWidget(top_row)

        # --- Notes area (hidden by default) ---
        self.notes_area = QTextEdit()
        self.notes_area.setPlaceholderText("Add notes...")
        self.notes_area.setPlainText(self.notes)
        self.notes_area.setMaximumHeight(80)
        self.notes_area.setVisible(False)
        self.notes_area.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                color: rgba(255, 255, 255, 0.7);
                font-size: {Theme.px(Theme.FONT_TITLE)}px;
                font-family: 'Segoe UI';
                padding: 6px 10px;
                margin: 0 10px 6px 46px;
            }}
            QTextEdit:focus {{
                border-color: rgba(255, 255, 255, 0.15);
            }}
        """)
        self.notes_area.focusOutEvent = self._notes_focus_out
        self.outer_layout.addWidget(self.notes_area)

        # Apply completed style
        self._apply_done_style(done)

        # Base hover style
        self.setStyleSheet(f"""
            TaskWidget {{
                background: rgba(255, 255, 255, 0.02);
                border-radius: 8px;
                border: 1px solid transparent;
            }}
            TaskWidget:hover {{
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.06);
            }}
        """)

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def _update_due_label(self):
        """Update the due date label with color-coded text."""
        if not self.due_date:
            self.due_label.setText("")
            self.due_label.setFixedWidth(0)
            return

        from datetime import date
        try:
            due = date.fromisoformat(self.due_date)
            today = date.today()
            delta = (due - today).days

            if delta < 0:
                color = "#FF6B6B"  # Red — overdue
                text = f"⚠ {due.strftime('%b %d')}"
            elif delta == 0:
                color = "#FFB347"  # Orange — due today
                text = "📅 Today"
            elif delta == 1:
                color = "#FFD93D"  # Yellow — tomorrow
                text = "📅 Tomorrow"
            elif delta <= 7:
                color = "rgba(255,255,255,0.5)"
                text = f"📅 {due.strftime('%a')}"
            else:
                color = "rgba(255,255,255,0.3)"
                text = f"📅 {due.strftime('%b %d')}"

            self.due_label.setText(text)
            self.due_label.setStyleSheet(f"color: {color}; font-size: {Theme.px(Theme.FONT_BODY)}px; background: transparent; padding: 0 4px;")
            self.due_label.setFixedWidth(self.due_label.sizeHint().width() + 8)
        except ValueError:
            self.due_label.setText("")
            self.due_label.setFixedWidth(0)

    def _apply_done_style(self, done: bool):
        """Visual feedback for completed/active tasks."""
        if done:
            self.task_label.setStyleSheet(
                f"color: rgba(255,255,255,0.28); text-decoration: line-through; font-size: {Theme.px(Theme.FONT_DISPLAY)}px; background: transparent;"
            )
            self.setProperty("taskDone", True)
        else:
            self.task_label.setStyleSheet(
                f"color: rgba(255,255,255,0.85); font-size: {Theme.px(Theme.FONT_DISPLAY)}px; background: transparent;"
            )
            self.setProperty("taskDone", False)

    def show_context_menu(self, position):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #1a1a2e;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 6px;
            }}
            QMenu::item {{
                color: #E8E8F0;
                padding: 8px 24px 8px 16px;
                border-radius: 6px;
                font-size: {Theme.px(Theme.FONT_HEADLINE)}px;
                font-family: "Segoe UI";
            }}
            QMenu::item:selected {{
                background: rgba(255,255,255,0.08);
                color: {self.accent_color};
            }}
            QMenu::separator {{
                height: 1px;
                background: rgba(255,255,255,0.06);
                margin: 4px 8px;
            }}
        """)
        edit_action = menu.addAction("✏️  Edit")
        notes_action = menu.addAction("📝  Notes")
        due_date_action = menu.addAction("📅  Due Date")
        if self.due_date:
            clear_due_action = menu.addAction("❌  Clear Due Date")
        else:
            clear_due_action = None
        menu.addSeparator()
        delete_action = menu.addAction("🗑️  Delete")

        action = menu.exec_(self.mapToGlobal(position))
        if action == delete_action and self.on_delete:
            self.on_delete(self.task_id)
        elif action == edit_action:
            self.start_editing()
        elif action == notes_action:
            self.toggle_notes()
        elif action == due_date_action:
            self._show_date_picker()
        elif clear_due_action and action == clear_due_action:
            self._set_due_date("")

    def toggle_notes(self):
        """Toggle notes area visibility."""
        self.notes_visible = not self.notes_visible
        self.notes_area.setVisible(self.notes_visible)
        if self.notes_visible:
            self.notes_area.setFocus()

    def _notes_focus_out(self, event):
        """Save notes when focus leaves the text area."""
        new_notes = self.notes_area.toPlainText()
        if new_notes != self.notes:
            self.notes = new_notes
            if self.on_notes_change:
                self.on_notes_change(self.task_id, new_notes)
        from PyQt5.QtWidgets import QTextEdit
        QTextEdit.focusOutEvent(self.notes_area, event)

    def _show_date_picker(self):
        """Show a premium date picker popup with dynamic sizing."""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout as QVBox,
                                     QHBoxLayout as QHBox, QSizeGrip)

        # ── Compute sizes dynamically from current font scale ────────
        scale = Theme._scale
        cell_w = round(48 * scale)
        cell_h = round(38 * scale)
        pad = round(18 * scale)          # container padding each side
        nav_h = round(44 * scale)        # navigation bar height
        title_h = round(40 * scale)      # title row height
        bottom_h = round(44 * scale)     # bottom row height
        grid_w = cell_w * 7 + 30         # 7 cols + margin buffer
        grid_h = cell_h * 6 + nav_h + 14 # 6 rows + nav + spacing
        dlg_w = grid_w + pad * 2 + 40    # grid + padding + extra room
        dlg_h = grid_h + title_h + bottom_h + pad * 2 + 30

        dialog = QDialog(self)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setWindowTitle("Set Due Date")
        dialog.setMinimumSize(dlg_w, dlg_h)
        dialog.resize(dlg_w, dlg_h)

        # Main dialog layout — no fixed wrapper, stretches with resize
        dialog.setStyleSheet("""
            QDialog {
                background: #16162a;
                border: 1px solid rgba(255,255,255,0.08);
            }
        """)

        main_layout = QVBox(dialog)
        main_layout.setContentsMargins(pad, round(12 * scale), pad, pad)
        main_layout.setSpacing(round(8 * scale))

        # Title bar
        title_row = QHBox()
        title_label = QLabel("📅  Set Due Date")
        title_label.setStyleSheet(f"""
            color: #E8E8F0; font-size: {Theme.px(Theme.FONT_BODY_SM)}px; font-weight: 600;
            font-family: 'Segoe UI'; background: transparent;
        """)
        title_row.addWidget(title_label)
        title_row.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: rgba(255,255,255,0.4);
                border: none; font-size: {Theme.px(Theme.FONT_BODY_SM)}px; border-radius: 14px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.1); color: #FF6B6B;
            }}
        """)
        close_btn.clicked.connect(dialog.reject)
        title_row.addWidget(close_btn)
        main_layout.addLayout(title_row)

        # Separator
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.06);")
        main_layout.addWidget(sep)

        # Calendar
        calendar = QCalendarWidget()
        calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        calendar.setStyleSheet(f"""
            /* Main calendar background */
            QCalendarWidget {{
                background: transparent;
                border: none;
            }}

            /* Navigation bar (month/year header) */
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background: rgba(255,255,255,0.03);
                border-radius: 10px;
                padding: 4px;
                min-height: {nav_h}px;
            }}

            /* Month/Year label */
            #qt_calendar_monthbutton, #qt_calendar_yearbutton {{
                color: #E8E8F0;
                font-size: {Theme.px(Theme.FONT_CAL_NAV)}px;
                font-weight: 600;
                font-family: 'Segoe UI';
                padding: 4px 10px;
                border: none;
                background: transparent;
            }}
            #qt_calendar_monthbutton:hover, #qt_calendar_yearbutton:hover {{
                background: rgba(255,255,255,0.08);
                border-radius: 6px;
            }}

            /* Previous/Next month buttons */
            #qt_calendar_prevmonth, #qt_calendar_nextmonth {{
                border: none;
                qproperty-icon: none;
                background: transparent;
                color: rgba(255,255,255,0.5);
                font-size: {Theme.px(Theme.FONT_TITLE)}px;
                min-width: {round(32 * scale)}px;
                min-height: {round(32 * scale)}px;
                border-radius: 8px;
            }}
            #qt_calendar_prevmonth {{
                qproperty-text: "◀";
            }}
            #qt_calendar_nextmonth {{
                qproperty-text: "▶";
            }}
            #qt_calendar_prevmonth:hover, #qt_calendar_nextmonth:hover {{
                background: rgba(78, 205, 196, 0.15);
                color: {self.accent_color};
            }}

            /* Year spin box */
            QCalendarWidget QSpinBox {{
                color: #E8E8F0;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 2px 6px;
                font-size: {Theme.px(Theme.FONT_CAPTION)}px;
                selection-background-color: {self.accent_color};
            }}
            QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {{
                width: 18px;
                border: none;
                background: transparent;
            }}

            /* Day grid */
            QCalendarWidget QAbstractItemView {{
                background: transparent;
                color: rgba(255,255,255,0.8);
                font-size: {Theme.px(Theme.FONT_CAPTION)}px;
                font-family: 'Segoe UI';
                selection-background-color: {self.accent_color};
                selection-color: white;
                border: none;
                outline: none;
                gridline-color: transparent;
            }}

            /* Individual day cells — scaled dynamically */
            QCalendarWidget QAbstractItemView::item {{
                width: {cell_w}px;
                height: {cell_h}px;
                border-radius: {round(8 * scale)}px;
                margin: 1px;
            }}
            QCalendarWidget QAbstractItemView::item:hover {{
                background: rgba(78, 205, 196, 0.2);
                color: white;
            }}
            QCalendarWidget QAbstractItemView::item:selected {{
                background: {self.accent_color};
                color: white;
                font-weight: bold;
            }}

            /* Weekday header row */
            QCalendarWidget QWidget {{
                alternate-background-color: transparent;
            }}

            /* Month dropdown menu */
            QCalendarWidget QMenu {{
                background: #1a1a2e;
                color: #E8E8F0;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 4px;
            }}
            QCalendarWidget QMenu::item {{
                padding: 6px 16px;
                border-radius: 4px;
            }}
            QCalendarWidget QMenu::item:selected {{
                background: rgba(78, 205, 196, 0.25);
                color: white;
            }}

            /* Navigation bar buttons */
            QCalendarWidget QToolButton {{
                color: rgba(255,255,255,0.6);
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 4px;
                font-size: {Theme.px(Theme.FONT_CAPTION)}px;
            }}
            QCalendarWidget QToolButton:hover {{
                background: rgba(255,255,255,0.08);
                color: #E8E8F0;
            }}
            QCalendarWidget QToolButton::menu-indicator {{
                image: none;
                width: 0;
            }}
        """)

        if self.due_date:
            try:
                calendar.setSelectedDate(QDate.fromString(self.due_date, "yyyy-MM-dd"))
            except Exception:
                pass
        calendar.clicked.connect(lambda date: self._on_date_selected(date, dialog))
        main_layout.addWidget(calendar, stretch=1)

        # Bottom row: Clear button + resize grip
        bottom = QHBox()
        bottom.addStretch()
        if self.due_date:
            clear_btn = QPushButton("Clear Date")
            clear_btn.setCursor(Qt.PointingHandCursor)
            clear_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: rgba(255,255,255,0.4);
                    border: 1px solid rgba(255,255,255,0.08); border-radius: 6px;
                    padding: 6px 16px; font-size: {Theme.px(Theme.FONT_CAPTION_SM)}px; font-family: 'Segoe UI';
                }}
                QPushButton:hover {{
                    color: #FF6B6B; border-color: rgba(255,107,107,0.3);
                    background: rgba(255,107,107,0.08);
                }}
            """)
            clear_btn.clicked.connect(lambda: (self._set_due_date(''), dialog.accept()))
            bottom.addWidget(clear_btn)

        # Resize grip in the corner
        grip = QSizeGrip(dialog)
        grip.setStyleSheet("background: transparent;")
        grip.setFixedSize(16, 16)
        bottom.addWidget(grip, alignment=Qt.AlignBottom | Qt.AlignRight)
        main_layout.addLayout(bottom)

        dialog.exec_()

    def _on_date_selected(self, date: QDate, dialog):
        """Handle date selection from calendar."""
        date_str = date.toString("yyyy-MM-dd")
        self._set_due_date(date_str)
        dialog.accept()

    def _set_due_date(self, date_str: str):
        """Set the due date and notify."""
        old_date = self.due_date
        self.due_date = date_str
        self._update_due_label()
        if self.on_due_date_change:
            self.on_due_date_change(self.task_id, date_str, old_date)

    def start_editing(self):
        self.editing = True
        self.task_label.hide()
        self.edit_input.setText(self.description)
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
                if self.on_edit:
                    self.on_edit(self.task_id, new_text)
            self.edit_input.hide()
            self.task_label.show()

    def focusOutEvent(self, event):
        if self.editing:
            self.finish_editing()
        super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Double-click toggles notes panel."""
        if event.button() == Qt.LeftButton:
            self.toggle_notes()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if not hasattr(self, 'drag_start_position'):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"{self.task_id}|{self.quadrant_name}")
        drag.setMimeData(mime_data)

        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setOpacity(0.65)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        drag.exec_(Qt.MoveAction)
        self.setCursor(Qt.OpenHandCursor)
