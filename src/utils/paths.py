"""Утилиты для работы с путями в приложении."""
import os
import sys


def get_app_dir() -> str:
    """Возвращает папку приложения (работает и в .exe, и в .py)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_data_file_path(filename: str = "tasks.json") -> str:
    """Возвращает полный путь к файлу данных."""
    return os.path.join(get_app_dir(), filename)