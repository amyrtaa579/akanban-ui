"""Точка входа в приложение AKanban."""
import sys
import os

# Добавляем корень проекта в sys.path, чтобы импорты из src/ работали
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from ui.main_window import AKanban

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AKanban()
    window.show()
    sys.exit(app.exec())