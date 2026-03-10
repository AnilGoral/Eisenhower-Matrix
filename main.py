import sys
import os
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import EisenhowerMatrixApp


def get_app_data_dir():
    """Get the application data directory (cross-platform)."""
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    elif sys.platform == 'darwin':
        base = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    else:
        base = os.environ.get('XDG_DATA_HOME', os.path.join(os.path.expanduser('~'), '.local', 'share'))
    app_dir = os.path.join(base, 'EisenhowerMatrix')
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def main():
    app_data_dir = get_app_data_dir()
    app = QApplication(sys.argv)
    window = EisenhowerMatrixApp(app_data_dir=app_data_dir, resource_base=resource_path(''))
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()