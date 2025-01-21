import sys
import os
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import EisenhowerMatrixApp
from AppKit import NSBundle

def main():
    
    app = QApplication(sys.argv)
    window = EisenhowerMatrixApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 