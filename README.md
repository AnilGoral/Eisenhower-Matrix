<div align="center">

<img src="icon.png" alt="Eisenhower Matrix" width="100"/>

# Eisenhower Matrix

A modern desktop task manager built with Python & PyQt5.  
Organize tasks by **importance** and **urgency** using the proven Eisenhower method.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-41CD52?logo=qt&logoColor=white)](https://pypi.org/project/PyQt5/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](#)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **4-Quadrant Matrix** | Prioritize tasks across Do First, Schedule, Delegate, and Eliminate |
| **Drag & Drop** | Move tasks between quadrants or reorder within one |
| **Dark Glassmorphic UI** | Premium dark theme with gradient accents and hover animations |
| **Task Statistics** | Pie chart breakdown and per-quadrant completion rates |
| **Import / Export** | Save and load tasks as JSON or CSV |
| **System Tray** | Minimize to tray — quick access via right-click menu |
| **Persistent Settings** | Custom colors, opacity, and quadrant names saved across sessions |
| **Keyboard Shortcuts** | `Ctrl+N` new task · `Ctrl+S` settings · `Ctrl+T` stats · `Ctrl+Q` quit |

## 📸 The Matrix

| Quadrant | Color | Purpose |
|----------|-------|---------|
| 🔴 **Important & Urgent** | Coral | Do these immediately |
| 🟢 **Important but Not Urgent** | Teal | Schedule for later |
| 🟠 **Not Important but Urgent** | Orange | Delegate if possible |
| 🟢 **Not Important & Not Urgent** | Mint | Eliminate or do last |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** — [download here](https://python.org/downloads)
- **pip** (comes with Python)

### Install & Run

```bash
# Clone the repo
git clone https://github.com/yourusername/Eisenhower-Matrix.git
cd Eisenhower-Matrix

# Install dependencies
pip install -r requirements.txt

# Launch the app
python main.py
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `PyQt5` | ≥ 5.15 | GUI framework |
| `matplotlib` | ≥ 3.5 | Statistics pie chart |
| `pyinstaller` | ≥ 5.0 | Building standalone `.exe` (optional) |

---

## 🎯 Usage

### Adding Tasks
- Click the **+** button on any quadrant header
- Or **double-click** anywhere in a quadrant
- Type your task and press **Enter**

### Managing Tasks
- **Right-click** a task → Edit or Delete
- **Check the box** to mark a task complete (strikethrough + faded)
- **Drag & drop** tasks between quadrants or reorder them

### Settings (`Ctrl+S`)
- **Appearance** — background color, text color, window opacity
- **Quadrants** — rename any quadrant label
- **Data** — import/export tasks as JSON or CSV

### Statistics (`Ctrl+T`)
- Overview: total tasks created, completed, and active
- Per-quadrant: completion rate, average completion time
- Visual pie chart of task distribution

---

## 📁 Project Structure

```
Eisenhower-Matrix/
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
├── icon.png                         # App icon
├── eisenhower.spec                  # PyInstaller build spec
├── build_installer.bat              # Windows build script
├── installer.iss                    # Inno Setup installer config
└── src/
    ├── database/
    │   └── db_manager.py            # SQLite task storage
    ├── ui/
    │   ├── main_window.py           # Main window + stylesheet
    │   ├── widgets/
    │   │   ├── quadrant_widget.py   # Quadrant card (header, scroll, tasks)
    │   │   └── task_widget.py       # Single task (checkbox, label, drag)
    │   └── dialogs/
    │       ├── settings_dialog.py   # Settings tabs (appearance, data, names)
    │       └── statistics_dialog.py # Stats cards + pie chart
    └── utils/
        ├── constants.py             # App-wide constants
        ├── settings_manager.py      # JSON settings persistence
        └── data_manager.py          # JSON/CSV import & export
```

---

## 🏗️ Building a Standalone Executable

### Quick Build (PyInstaller)

```bash
pyinstaller eisenhower.spec
```

The `.exe` will be in `dist/EisenhowerMatrix/`.

### Full Installer (Inno Setup)

```bash
# Runs PyInstaller + Inno Setup in sequence
build_installer.bat
```

Requires [Inno Setup](https://jrsoftware.org/isinfo.php) to be installed.

---

## 💾 Data Storage

| Item | Location |
|------|----------|
| **Database** | `%APPDATA%\EisenhowerMatrix\tasks.db` |
| **Settings** | `%APPDATA%\EisenhowerMatrix\settings.json` |
| **Exports** | `%APPDATA%\EisenhowerMatrix\exports\` |

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Add new task (to first quadrant) |
| `Ctrl+S` | Open settings |
| `Ctrl+T` | Open statistics |
| `Ctrl+Q` | Quit application |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📬 Contact

**Anil Goral** — goralanil@gmail.com

---

<div align="center">
  <sub>Built with ❤️ using Python & PyQt5</sub>
</div>
