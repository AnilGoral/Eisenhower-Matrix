from PyQt5.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QColorDialog, QSpinBox,
                            QLineEdit, QFormLayout, QComboBox, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class SettingsDialog(QDialog):
    def __init__(self, parent=None, bg_color=None, text_color=None, opacity=None, quadrant_names=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self.parent = parent
        
        # Store default values for reset
        self.default_bg_color = QColor("#646464")
        self.default_text_color = QColor("#FFFFFF")
        self.default_opacity = 95
        
        # Use provided colors or defaults
        self.current_bg_color = bg_color or self.default_bg_color
        self.current_text_color = text_color or self.default_text_color
        self.current_opacity = opacity or self.default_opacity
        
        self.setup_ui(quadrant_names)

    def setup_ui(self, quadrant_names):
        layout = QVBoxLayout(self)

        # Create tab widget
        self.tabs = QTabWidget()
        self.appearance_tab = AppearanceTab(
            self.current_bg_color,
            self.current_text_color,
            self.current_opacity
        )
        self.quadrants_tab = QuadrantsTab(quadrant_names)
        self.data_tab = DataTab(self.parent)  # Add new Data tab
        
        self.tabs.addTab(self.appearance_tab, "Appearance")
        self.tabs.addTab(self.quadrants_tab, "Quadrants")
        self.tabs.addTab(self.data_tab, "Data")
        layout.addWidget(self.tabs)

        # Add buttons
        buttons_layout = QHBoxLayout()
        
        # Add reset button
        reset_button = QPushButton("Reset to Default")
        reset_button.clicked.connect(self.reset_to_default)
        buttons_layout.addWidget(reset_button)
        
        buttons_layout.addStretch()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

    def reset_to_default(self):
        # Reset appearance tab to default values
        self.appearance_tab.reset_to_default(
            self.default_bg_color,
            self.default_text_color,
            self.default_opacity
        )
        # Reset quadrant names
        self.quadrants_tab.reset_names()

    def save_settings(self):
        self.accept()


class AppearanceTab(QWidget):
    def __init__(self, bg_color, text_color, opacity):
        super().__init__()
        self.current_bg_color = bg_color
        self.current_text_color = text_color
        self.current_opacity = opacity
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Colors Section
        colors_group = QWidget()
        colors_layout = QFormLayout(colors_group)
        
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedWidth(100)
        self.bg_color_btn.clicked.connect(lambda: self.choose_color("background"))
        colors_layout.addRow("Background Color:", self.bg_color_btn)

        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedWidth(100)
        self.text_color_btn.clicked.connect(lambda: self.choose_color("text"))
        colors_layout.addRow("Text Color:", self.text_color_btn)

        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setValue(self.current_opacity)
        colors_layout.addRow("Opacity (%):", self.opacity_spin)

        layout.addWidget(colors_group)
        layout.addStretch()
        
        # Set initial colors
        self.update_color_preview("background", self.current_bg_color)
        self.update_color_preview("text", self.current_text_color)

    def choose_color(self, color_type):
        current_color = self.current_bg_color if color_type == "background" else self.current_text_color
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            if color_type == "background":
                self.current_bg_color = color
            else:
                self.current_text_color = color
            self.update_color_preview(color_type, color)

    def update_color_preview(self, color_type, color):
        button = self.bg_color_btn if color_type == "background" else self.text_color_btn
        button.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #888;"
        )

    def reset_to_default(self, bg_color, text_color, opacity):
        self.current_bg_color = bg_color
        self.current_text_color = text_color
        self.opacity_spin.setValue(opacity)
        self.update_color_preview("background", bg_color)
        self.update_color_preview("text", text_color)


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
        
        # Quadrant name inputs
        form_layout = QFormLayout()
        self.quadrant_inputs = []
        
        for i, name in enumerate(self.current_names, 1):
            input_field = QLineEdit(name)
            form_layout.addRow(f"Quadrant {i}:", input_field)
            self.quadrant_inputs.append(input_field)
        
        layout.addLayout(form_layout)
        
        # Reset names button
        reset_names_btn = QPushButton("Reset Quadrant Names")
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
        
        # Export section
        export_group = QWidget()
        export_layout = QVBoxLayout(export_group)
        
        export_label = QLabel("Export Tasks")
        export_label.setStyleSheet("font-weight: bold;")
        export_layout.addWidget(export_label)
        
        export_json_btn = QPushButton("Export to JSON")
        export_json_btn.clicked.connect(self.main_window.export_to_json)
        export_layout.addWidget(export_json_btn)
        
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self.main_window.export_to_csv)
        export_layout.addWidget(export_csv_btn)
        
        layout.addWidget(export_group)
        
        # Import section
        import_group = QWidget()
        import_layout = QVBoxLayout(import_group)
        
        import_label = QLabel("Import Tasks")
        import_label.setStyleSheet("font-weight: bold;")
        import_layout.addWidget(import_label)
        
        import_json_btn = QPushButton("Import from JSON")
        import_json_btn.clicked.connect(self.main_window.import_from_json)
        import_layout.addWidget(import_json_btn)
        
        import_csv_btn = QPushButton("Import from CSV")
        import_csv_btn.clicked.connect(self.main_window.import_from_csv)
        import_layout.addWidget(import_csv_btn)
        
        layout.addWidget(import_group)
        layout.addStretch() 