from typing import List

WINDOW_TITLE = "Eisenhower Matrix Widget"
WINDOW_SIZE = (400, 400)
WINDOW_POSITION = (100, 100)

QUADRANT_NAMES: List[str] = [
    "Important & Urgent",
    "Important but Not Urgent",
    "Not Important but Urgent",
    "Not Important & Not Urgent"
]

STYLE_SHEET = """
    QWidget {
        background: rgba(100, 100, 100, 0.95);
        border-radius: 5px;
    }
    QLabel {
        color: #FFFFFF;
        font-size: 14px;
        font-weight: bold;
    }
    QLineEdit {
        font-size: 11px;
        color: #FFFFFF;
    }
    QCheckBox {
        spacing: 5px;
    }
    QCheckBox::indicator {
        width: 12px;
        height: 12px;
        background-color: white;
        border: 1px solid gray;
        border-radius: 2px;
    }
    QCheckBox::indicator:checked {
        background-color: #4CAF50;
        border: 1px solid #4CAF50;
    }
"""

TASK_LABEL_STYLE = "font-size: 11px; color: #FFFFFF;"
QUADRANT_MARGINS = (5, 5, 5, 5)
TASK_MARGINS = (5, 2, 5, 2)
TASK_SPACING = 2 