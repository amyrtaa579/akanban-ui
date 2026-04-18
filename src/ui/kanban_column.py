"""Виджет колонки канбан-доски."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt


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