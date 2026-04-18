import sys
import json
import os
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag

class TaskCard(QWidget):
    def __init__(self, task_data: dict, status: str, app_ref):
        super().__init__()
        self.task_id = task_data["id"]
        self.text = task_data["text"]
        self.status = status
        self.app_ref = app_ref

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.lbl = QLabel(self.text)
        self.lbl.setStyleSheet("""
            QLabel {
                background-color: white; padding: 8px; border-radius: 4px;
                border-left: 4px solid #3498db;
            }
            QLabel:hover {
                background-color: #f8f9fa; border-left-color: #2980b9;
            }
        """)
        self.lbl.setWordWrap(True)
        self.lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.lbl.setCursor(Qt.OpenHandCursor)

        self.editor = QLineEdit(self.text)
        self.editor.setVisible(False)
        self.editor.setStyleSheet("""
            background-color: white; padding: 8px; border-radius: 4px;
            border: 2px solid #3498db;
        """)
        self.editor.returnPressed.connect(self._save_edit)

        del_btn = QPushButton("❌")
        del_btn.setFixedSize(24, 24)
        del_btn.setStyleSheet("""
            background-color: #e74c3c; color: white; border: none; border-radius: 12px;
        """)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda: app_ref.delete_task(self.status, self.task_id))

        layout.addWidget(self.lbl)
        layout.addWidget(self.editor)
        layout.addWidget(del_btn)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self.editor.isHidden():
            self.lbl.setVisible(False)
            self.editor.setVisible(True)
            self.editor.setFocus()
            self.editor.selectAll()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._cancel_edit()
        else:
            super().keyPressEvent(event)

    def _save_edit(self):
        new_text = self.editor.text().strip()
        if new_text and new_text != self.text:
            self.app_ref.edit_task(self.status, self.task_id, new_text)
            self.text = new_text
            self.lbl.setText(new_text)
        self._reset_view()

    def _cancel_edit(self):
        self.editor.setText(self.text)
        self._reset_view()

    def _reset_view(self):
        self.editor.clearFocus()
        self.editor.setVisible(False)
        self.lbl.setVisible(True)

    def mousePressEvent(self, event):
        if self.editor.isHidden() and event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"{self.status}|{self.task_id}")
            drag.setMimeData(mime)
            drag.exec(Qt.MoveAction)

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

        self.setStyleSheet("""
            QMainWindow { font-family: 'Segoe UI', 'Roboto', sans-serif; }
            QLineEdit { padding: 8px; border-radius: 6px; border: 1px solid #ccc; }
            QPushButton { border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #27ae60; }
        """)

        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")
        self.tasks = self.load_tasks()

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

    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key in ["надо", "делаю", "готово"]:
                        if key not in data:
                            data[key] = []
                        if data[key] and isinstance(data[key][0], str):
                            data[key] = [{"id": int(time.time() + i), "text": t} for i, t in enumerate(data[key])]
                    return data
            except Exception:
                pass
        return {"надо": [], "делаю": [], "готово": []}

    def save_tasks(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

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
            new_task = {"id": int(time.time() * 1000), "text": text}
            self.tasks["надо"].append(new_task)
            self.save_tasks()
            self.render_tasks()
            self.task_input.clear()
            self.task_input.setFocus()

    def delete_task(self, status, task_id):
        self.tasks[status] = [t for t in self.tasks[status] if t["id"] != task_id]
        self.save_tasks()
        self.render_tasks()

    def move_task(self, old_status, new_status, task_id):
        task_to_move = None
        for t in self.tasks[old_status]:
            if t["id"] == task_id:
                task_to_move = t
                break
        if task_to_move:
            self.tasks[old_status].remove(task_to_move)
            self.tasks[new_status].append(task_to_move)
            self.save_tasks()
            self.render_tasks()

    def edit_task(self, status, task_id, new_text):
        for t in self.tasks[status]:
            if t["id"] == task_id:
                t["text"] = new_text
                break
        self.save_tasks()

    def closeEvent(self, event):
        self.save_tasks()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AKanban()
    window.show()
    sys.exit(app.exec())