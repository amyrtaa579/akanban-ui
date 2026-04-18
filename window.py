import json
import os
import time

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag

from utils.paths import get_data_file_path
from core.data_store import DataStore
from ui.task_card import TaskCard

class KanbanColumn(QWidget):
    def __init__(self, title: str, status_key: str, app_ref):
        super().__init__()
        self.status_key = status_key
        self.app_ref = app_ref

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(10)

        header = QLabel(title)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 18px; font-weight: bold; color: #fff;
            background-color: #2c3e50; padding: 10px; border-radius: 6px;
        """)
        self.main_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content_widget = QWidget()
        scroll.setWidget(content_widget)

        self.task_layout = QVBoxLayout(content_widget)
        self.task_layout.setSpacing(5)
        self.task_layout.addStretch()
        self.main_layout.addWidget(scroll)

        self.setStyleSheet("background-color: #ecf0f1; border-radius: 8px;")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()
        data = event.mimeData().text()
        if "|" in data:
            old_status, task_id_str = data.split("|", 1)
            if old_status != self.status_key:
                try:
                    task_id = int(task_id_str)
                    self.app_ref.move_task(old_status, self.status_key, task_id)
                except ValueError:
                    pass

class AKanban(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AKanban")
        self.resize(900, 500)

        # 🆕 Меню "Справка" со ссылкой на репозиторий
        self._setup_help_menu()

        self.setStyleSheet("""
            QMainWindow { font-family: 'Segoe UI', 'Roboto', sans-serif; }
            QLineEdit { padding: 8px; border-radius: 6px; border: 1px solid #ccc; }
            QPushButton { border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #27ae60; }
        """)

        self.store = DataStore("tasks.json")
        self.tasks = self.store.data  # 🆕 Берём данные из кэша

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.columns = {}
        for name, key in [("Надо", "надо"), ("Делаю", "делаю"), ("Готово", "готово")]:
            col = KanbanColumn(name, key, self)
            self.columns[key] = col
            main_layout.addWidget(col)

        add_widget = QWidget()
        add_layout = QHBoxLayout(add_widget)
        add_layout.setContentsMargins(0, 0, 0, 0)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Новая задача...")
        add_btn = QPushButton("➕")
        add_btn.setFixedWidth(40)

        add_layout.addWidget(self.task_input)
        add_layout.addWidget(add_btn)
        self.columns["надо"].main_layout.insertWidget(1, add_widget)

        add_btn.clicked.connect(self.add_task)
        self.task_input.returnPressed.connect(self.add_task)

        self.render_tasks()


    def render_tasks(self):
        for col in self.columns.values():
            while col.task_layout.count() > 0:
                item = col.task_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        for status, items in self.tasks.items():
            for task_data in items:
                card = TaskCard(task_data, status, self)
                self.columns[status].task_layout.addWidget(card)

    def add_task(self):
        text = self.task_input.text().strip()
        if text:
            self.store.add_task("надо", text)
            self.tasks = self.store.load()  # Перезагружаем актуальные данные
            self.render_tasks()
            self.task_input.clear()
            self.task_input.setFocus()

    def delete_task(self, status, task_id):
        self.store.delete_task(status, task_id)
        self.tasks = self.store.load()
        self.render_tasks()

    def move_task(self, old_status, new_status, task_id):
        # 🆕 Делегируем логику хранилищу
        if self.store.move_task(old_status, new_status, task_id):
            self.tasks = self.store.load()  # Перезагружаем актуальные данные
            self.render_tasks()

    def edit_task(self, status, task_id, new_text):
        # 🆕 Делегируем логику хранилищу
        if self.store.edit_task(status, task_id, new_text):
            self.tasks = self.store.load()
            self.render_tasks()

    def closeEvent(self, event):
        # 🆕 Данные уже сохраняются после каждой операции в DataStore,
        # поэтому здесь ничего делать не нужно
        event.accept()

    def _setup_help_menu(self):
        """Создаёт меню Справка с информацией и ссылкой на GitHub"""
        from PySide6.QtWidgets import QMenuBar, QMessageBox
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Справка")
        
        # Пункт "О программе"
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(lambda: QMessageBox.information(
            self, 
            "О AKanban", 
            "AKanban v1.0\n\n"
            "Персональное Kanban-приложение для управления задачами.\n"
            "Написано на Python + PySide6.\n\n"
            "GitHub: github.com/amyrtaa579/akanban-ui"
        ))
        
        # Пункт "Открыть на GitHub"
        github_action = help_menu.addAction("Открыть на GitHub")
        github_action.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/amyrtaa579/akanban-ui")
        ))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AKanban()
    window.show()
    sys.exit(app.exec())