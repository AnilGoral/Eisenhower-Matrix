from PyQt5.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout,
                            QPushButton, QLabel, QColorDialog, QSpinBox,
                            QLineEdit, QFormLayout, QHBoxLayout, QCheckBox,
                            QSlider)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from src.ui.theme import Theme


class SettingsDialog(QDialog):
    def __init__(self, parent=None, bg_color=None, text_color=None, opacity=None, quadrant_names=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(440)
        self.setMinimumHeight(320)
        self.main_window = parent

        # Store default values for reset (must match settings_manager defaults)
        self.default_bg_color = QColor("#0f0f1a")
        self.default_text_color = QColor("#E8E8F0")
        self.default_opacity = 97

        # Use provided colors or defaults
        self.current_bg_color = bg_color or self.default_bg_color
        self.current_text_color = text_color or self.default_text_color
        self.current_opacity = opacity or self.default_opacity

        self.setup_ui(quadrant_names)
        self.setStyleSheet(Theme.dialog_stylesheet())

    def setup_ui(self, quadrant_names):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Create tab widget
        self.tabs = QTabWidget()
        settings_mgr = self.main_window.settings_mgr if self.main_window else None
        self.appearance_tab = AppearanceTab(
            self.current_bg_color,
            self.current_text_color,
            self.current_opacity,
            settings_mgr=settings_mgr
        )
        self.quadrants_tab = QuadrantsTab(quadrant_names)
        self.data_tab = DataTab(self.main_window)

        self.tabs.addTab(self.appearance_tab, "  Appearance  ")
        self.tabs.addTab(self.quadrants_tab, "  Quadrants  ")
        self.tabs.addTab(self.data_tab, "  Data  ")
        layout.addWidget(self.tabs)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        reset_button = QPushButton("Reset to Default")
        reset_button.setCursor(Qt.PointingHandCursor)
        reset_button.setStyleSheet("""
            QPushButton {
                color: rgba(255,255,255,0.5);
                background: transparent;
                border: 1px solid rgba(255,255,255,0.08);
            }
            QPushButton:hover {
                color: #E74C3C;
                border-color: rgba(231,76,60,0.3);
                background: rgba(231,76,60,0.08);
            }
        """)
        reset_button.clicked.connect(self.reset_to_default)
        buttons_layout.addWidget(reset_button)

        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        save_button = QPushButton("  Save  ")
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setStyleSheet("""
            QPushButton {
                background: #3498DB;
                border: none;
                color: white;
                font-weight: bold;
                padding: 8px 24px;
            }
            QPushButton:hover {
                background: #2980B9;
            }
        """)
        save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_button)

        layout.addLayout(buttons_layout)

    def reset_to_default(self):
        self.appearance_tab.reset_to_default(
            self.default_bg_color,
            self.default_text_color,
            self.default_opacity
        )
        self.quadrants_tab.reset_names()

    def save_settings(self):
        self.accept()


class AppearanceTab(QWidget):
    def __init__(self, bg_color, text_color, opacity, settings_mgr=None):
        super().__init__()
        self.current_bg_color = bg_color
        self.current_text_color = text_color
        self.current_opacity = opacity
        self.settings_mgr = settings_mgr
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Section title
        section = QLabel("Colors & Transparency")
        section.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.DemiBold))
        section.setStyleSheet(f"color: #E8E8F0; font-size: {Theme.px(Theme.FONT_TITLE)}px; font-weight: 600; margin-bottom: 4px;")
        layout.addWidget(section)

        # Color controls
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(80, 30)
        self.bg_color_btn.setCursor(Qt.PointingHandCursor)
        self.bg_color_btn.clicked.connect(lambda: self.choose_color("background"))
        form.addRow("Background:", self.bg_color_btn)

        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedSize(80, 30)
        self.text_color_btn.setCursor(Qt.PointingHandCursor)
        self.text_color_btn.clicked.connect(lambda: self.choose_color("text"))
        form.addRow("Text Color:", self.text_color_btn)

        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(30, 100)
        self.opacity_spin.setValue(self.current_opacity)
        self.opacity_spin.setSuffix("%")
        self.opacity_spin.setFixedWidth(80)
        form.addRow("Opacity:", self.opacity_spin)

        layout.addLayout(form)

        # ── Font Scale section ──
        font_section = QLabel("Font Scale")
        font_section.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.DemiBold))
        font_section.setStyleSheet(f"color: #E8E8F0; font-size: {Theme.px(Theme.FONT_TITLE)}px; font-weight: 600; margin-top: 8px;")
        layout.addWidget(font_section)

        scale_row = QHBoxLayout()
        scale_row.setSpacing(12)

        self.font_scale_slider = QSlider(Qt.Horizontal)
        self.font_scale_slider.setRange(80, 150)
        current_scale = Theme.get_scale()
        self.font_scale_slider.setValue(current_scale)
        self.font_scale_slider.setTickPosition(QSlider.TicksBelow)
        self.font_scale_slider.setTickInterval(10)
        self.font_scale_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: rgba(255,255,255,0.08);
                height: 6px; border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: #4ECDC4; width: 16px; height: 16px;
                margin: -5px 0; border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #5EDDD4;
            }}
            QSlider::sub-page:horizontal {{
                background: rgba(78, 205, 196, 0.4);
                border-radius: 3px;
            }}
        """)
        self.font_scale_slider.valueChanged.connect(self._on_scale_changed)
        scale_row.addWidget(self.font_scale_slider)

        self.font_scale_label = QLabel(f"{current_scale}%")
        self.font_scale_label.setFixedWidth(48)
        self.font_scale_label.setAlignment(Qt.AlignCenter)
        scale_row.addWidget(self.font_scale_label)

        layout.addLayout(scale_row)

        note = QLabel("Adjust the slider and click Save to apply.")
        note.setStyleSheet(f"color: rgba(255,255,255,0.35); font-size: {Theme.px(Theme.FONT_OVERLINE)}px; font-style: italic;")
        layout.addWidget(note)

        # Auto-start section
        startup_section = QLabel("Startup")
        startup_section.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.DemiBold))
        startup_section.setStyleSheet(f"color: #E8E8F0; font-size: {Theme.px(Theme.FONT_TITLE)}px; font-weight: 600; margin-top: 8px;")
        layout.addWidget(startup_section)

        self.auto_start_cb = QCheckBox("Start on Windows login")
        self.auto_start_cb.setStyleSheet(f"""
            QCheckBox {{ color: #E8E8F0; font-size: {Theme.px(Theme.FONT_BODY)}px; spacing: 8px; background: transparent; }}
            QCheckBox::indicator {{ width: 20px; height: 20px; border-radius: 4px;
                border: 2px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.06); }}
            QCheckBox::indicator:checked {{ background: #4ECDC4; border-color: #4ECDC4; }}
            QCheckBox::indicator:hover {{ border-color: rgba(78,205,196,0.6); }}
        """)
        # Load current value
        auto_start = False
        if self.settings_mgr:
            auto_start = self.settings_mgr.settings.get('auto_start', False)
        self.auto_start_cb.setChecked(auto_start)
        self.auto_start_cb.stateChanged.connect(self._toggle_auto_start)
        layout.addWidget(self.auto_start_cb)

        layout.addStretch()

        # Set initial color previews
        self.update_color_preview("background", self.current_bg_color)
        self.update_color_preview("text", self.current_text_color)

    def _on_scale_changed(self, value):
        self.font_scale_label.setText(f"{value}%")

    def choose_color(self, color_type):
        current_color = self.current_bg_color if color_type == "background" else self.current_text_color
        color = QColorDialog.getColor(current_color, self)
        if color.isValid():
            if color_type == "background":
                self.current_bg_color = color
            else:
                self.current_text_color = color
            self.update_color_preview(color_type, color)

    def update_color_preview(self, color_type, color):
        button = self.bg_color_btn if color_type == "background" else self.text_color_btn
        button.setStyleSheet(
            f"background-color: {color.name()}; border: 2px solid rgba(255,255,255,0.15); border-radius: 5px;"
        )

    def reset_to_default(self, bg_color, text_color, opacity):
        self.current_bg_color = bg_color
        self.current_text_color = text_color
        self.opacity_spin.setValue(opacity)
        self.update_color_preview("background", bg_color)
        self.update_color_preview("text", text_color)
        self.font_scale_slider.setValue(100)
        self.auto_start_cb.setChecked(False)
        self._toggle_auto_start(Qt.Unchecked)

    def _toggle_auto_start(self, state):
        """Toggle auto-start via Windows Registry."""
        import sys
        enabled = (state == Qt.Checked) if isinstance(state, int) else bool(state)
        app_name = "EisenhowerMatrix"

        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            ) as key:
                if enabled:
                    # Use the python executable path for dev, or the exe path for built app
                    exe_path = sys.executable
                    if getattr(sys, 'frozen', False):
                        exe_path = sys.executable
                    else:
                        # In dev mode, run the main.py script
                        import os
                        main_py = os.path.abspath(os.path.join(
                            os.path.dirname(__file__), '..', '..', 'main.py'
                        ))
                        exe_path = f'"{sys.executable}" "{main_py}"'
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                    except FileNotFoundError:
                        pass
        except Exception as e:
            print(f"Auto-start registry error: {e}")

        # Save to settings
        if self.settings_mgr:
            self.settings_mgr.settings['auto_start'] = enabled
            self.settings_mgr.save_settings()


class QuadrantsTab(QWidget):
    def __init__(self, current_names=None):
        super().__init__()
        self.default_names = [
            "Important & Urgent",
            "Important but Not Urgent",
            "Not Important but Urgent",
            "Not Important & Not Urgent"
        ]
        self.current_names = current_names or self.default_names.copy()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        section = QLabel("Quadrant Labels")
        section.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.DemiBold))
        section.setStyleSheet(f"color: #E8E8F0; font-size: {Theme.px(Theme.FONT_TITLE)}px; font-weight: 600; margin-bottom: 4px;")
        layout.addWidget(section)

        # Quadrant name inputs with colored indicators
        accent_colors = ["#FF6B6B", "#4ECDC4", "#FFB347", "#95E1D3"]
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.quadrant_inputs = []

        for i, (name, color) in enumerate(zip(self.current_names, accent_colors)):
            label = QLabel(f"  ● Quadrant {i + 1}:")
            label.setStyleSheet(f"color: {color}; font-weight: bold;")
            input_field = QLineEdit(name)
            form_layout.addRow(label, input_field)
            self.quadrant_inputs.append(input_field)

        layout.addLayout(form_layout)

        reset_names_btn = QPushButton("Reset Names")
        reset_names_btn.setCursor(Qt.PointingHandCursor)
        reset_names_btn.setFixedWidth(120)
        reset_names_btn.clicked.connect(self.reset_names)
        layout.addWidget(reset_names_btn)
        layout.addStretch()

    def reset_names(self):
        for input_field, default_name in zip(self.quadrant_inputs, self.default_names):
            input_field.setText(default_name)

    def get_quadrant_names(self):
        return [input_field.text() for input_field in self.quadrant_inputs]


class DataTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Export section
        export_label = QLabel("Export Tasks")
        export_label.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.DemiBold))
        export_label.setStyleSheet(f"color: #E8E8F0; font-size: {Theme.px(Theme.FONT_TITLE)}px; font-weight: 600;")
        layout.addWidget(export_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        export_json_btn = QPushButton("📄  Export to JSON")
        export_json_btn.setCursor(Qt.PointingHandCursor)
        export_json_btn.clicked.connect(self.main_window.export_to_json)
        btn_layout.addWidget(export_json_btn)

        export_csv_btn = QPushButton("📊  Export to CSV")
        export_csv_btn.setCursor(Qt.PointingHandCursor)
        export_csv_btn.clicked.connect(self.main_window.export_to_csv)
        btn_layout.addWidget(export_csv_btn)

        layout.addLayout(btn_layout)

        # Divider
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: rgba(255,255,255,0.08);")
        layout.addWidget(divider)

        # Import section
        import_label = QLabel("Import Tasks")
        import_label.setFont(Theme.font("Segoe UI", Theme.PT_TITLE, QFont.DemiBold))
        import_label.setStyleSheet(f"color: #E8E8F0; font-size: {Theme.px(Theme.FONT_TITLE)}px; font-weight: 600;")
        layout.addWidget(import_label)

        import_btn_layout = QHBoxLayout()
        import_btn_layout.setSpacing(8)

        import_json_btn = QPushButton("📥  Import from JSON")
        import_json_btn.setCursor(Qt.PointingHandCursor)
        import_json_btn.clicked.connect(self.main_window.import_from_json)
        import_btn_layout.addWidget(import_json_btn)

        import_csv_btn = QPushButton("📥  Import from CSV")
        import_csv_btn.setCursor(Qt.PointingHandCursor)
        import_csv_btn.clicked.connect(self.main_window.import_from_csv)
        import_btn_layout.addWidget(import_csv_btn)

        layout.addLayout(import_btn_layout)
        layout.addStretch()