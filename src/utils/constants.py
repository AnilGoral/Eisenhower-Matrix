from typing import List, Dict

WINDOW_TITLE = "Eisenhower Matrix"

QUADRANT_NAMES: List[str] = [
    "Important & Urgent",
    "Important but Not Urgent",
    "Not Important but Urgent",
    "Not Important & Not Urgent"
]

QUADRANT_ACCENTS: Dict[int, str] = {
    0: "#FF6B6B",  # Coral Red    — Important & Urgent
    1: "#4ECDC4",  # Teal         — Important but Not Urgent
    2: "#FFB347",  # Warm Orange  — Not Important but Urgent
    3: "#95E1D3",  # Mint Green   — Not Important & Not Urgent
}

QUADRANT_BG_TINTS: Dict[int, str] = {
    0: "rgba(255, 107, 107, 0.06)",
    1: "rgba(78, 205, 196, 0.06)",
    2: "rgba(255, 179, 71, 0.06)",
    3: "rgba(149, 225, 211, 0.06)",
}

QUADRANT_MARGINS = (6, 4, 6, 4)
TASK_MARGINS = (8, 4, 8, 4)
TASK_SPACING = 3