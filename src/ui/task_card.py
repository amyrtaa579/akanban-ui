"""Виджет карточки задачи."""
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton
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