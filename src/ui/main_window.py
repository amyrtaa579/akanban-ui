"""Главное окно приложения AKanban."""
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLineEdit, QPushButton, QMenuBar, QMessageBox
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from core.data_store import DataStore
from ui.task_card import TaskCard
from ui.kanban_column import KanbanColumn


class AKanban(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AKanban")
        self.resize(900, 500)

        self._setup_help_menu()

        self.setStyleSheet("""
            QMainWindow { font-family: 'Segoe UI', 'Roboto', sans-serif; }
            QLineEdit { padding: 8px; border-radius: 6px; border: 1px solid #ccc; }
            QPushButton { border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #27ae60; }
        """)

        self.store = DataStore("tasks.json")
        self.tasks = self.store.data

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
            self.tasks = self.store.data
            self.render_tasks()
            self.task_input.clear()
            self.task_input.setFocus()

    def delete_task(self, status, task_id):
        self.store.delete_task(status, task_id)
        self.tasks = self.store.data
        self.render_tasks()

    def move_task(self, old_status, new_status, task_id):
        if self.store.move_task(old_status, new_status, task_id):
            self.tasks = self.store.data
            self.render_tasks()

    def edit_task(self, status, task_id, new_text):
        if self.store.edit_task(status, task_id, new_text):
            self.tasks = self.store.data
            self.render_tasks()

    def closeEvent(self, event):
        event.accept()

    def _setup_help_menu(self):
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Справка")

        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(lambda: QMessageBox.information(
            self, "О AKanban",
            "AKanban v1.0\n\nПерсональное Kanban-приложение для управления задачами.\nНаписано на Python + PySide6.\n\nGitHub: github.com/amyrtaa579/akanban-ui"
        ))

        github_action = help_menu.addAction("Открыть на GitHub")
        github_action.triggered.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/amyrtaa579/akanban-ui")
        ))