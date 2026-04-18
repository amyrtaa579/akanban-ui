"""Модуль для работы с данными: загрузка, сохранение, миграция."""
import json
import os
import time
from typing import Dict, List, Any

from utils.paths import get_data_file_path


class DataStore:
    """Управляет хранением задач в JSON-файле."""
    
    def __init__(self, filename: str = "tasks.json"):
        self.file_path = get_data_file_path(filename)
        # 🆕 Сразу загружаем данные из файла в кэш
        self.data = self.load()
    
    def _load_default(self) -> Dict[str, List[Dict[str, Any]]]:
        """Возвращает пустую структуру данных."""
        return {"надо": [], "делаю": [], "готово": []}
    
    def load(self) -> Dict[str, List[Dict[str, Any]]]:
        """Загружает данные из файла или возвращает пустую структуру."""
        if not os.path.exists(self.file_path):
            return self._load_default()
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Миграция: старый формат (строки) → новый (объекты с id)
                for key in ["надо", "делаю", "готово"]:
                    # ✅ ИСПРАВЛЕНО: добавлено 'data' после 'in'
                    if key not in data:
                        data[key] = []
                    if data[key] and isinstance(data[key][0], str):
                        data[key] = [
                            {"id": int(time.time() + i), "text": t} 
                            for i, t in enumerate(data[key])
                        ]
                # 🆕 Обновляем внутренний кэш
                self.data = data
                return data
        except Exception:
            return self._load_default()
    
    def save(self) -> bool:
        """Сохраняет внутренний кэш self.data в файл."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    # --- Методы для работы с задачами ---
    
    def add_task(self, status: str, text: str) -> Dict[str, Any]:
        """Добавляет задачу в указанную колонку."""
        task = {"id": int(time.time() * 1000), "text": text}
        self.data[status].append(task)
        self.save()
        return task
    
    def delete_task(self, status: str, task_id: int) -> bool:
        """Удаляет задачу по ID."""
        before = len(self.data[status])
        self.data[status] = [t for t in self.data[status] if t["id"] != task_id]
        if len(self.data[status]) < before:
            self.save()
            return True
        return False
    
    def move_task(self, old_status: str, new_status: str, task_id: int) -> bool:
        """Перемещает задачу между колонками."""
        task = next((t for t in self.data[old_status] if t["id"] == task_id), None)
        if task:
            self.data[old_status].remove(task)
            self.data[new_status].append(task)
            self.save()
            return True
        return False
    
    def edit_task(self, status: str, task_id: int, new_text: str) -> bool:
        """Редактирует текст задачи."""
        for t in self.data[status]:
            if t["id"] == task_id:
                t["text"] = new_text
                self.save()
                return True
        return False
    
    def get_tasks(self, status: str) -> List[Dict[str, Any]]:
        """Возвращает список задач для указанной колонки."""
        return self.data.get(status, [])