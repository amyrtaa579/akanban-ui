# AKanban

Персональное Kanban-приложение для управления задачами. Написано на Python + PySide6.

## Возможности
- Drag-and-drop перемещение задач между колонками
- Быстрое добавление, удаление и редактирование (двойной клик)
- Автосохранение в JSON
- Чистый интерфейс с hover-эффектами и прокруткой

## Установка и запуск
```bash
# 1. Клонировать репозиторий
git clone https://github.com/ТВОЙ_НИК/AKanban.git
cd AKanban

# 2. Создать окружение и установить зависимости
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install PySide6

# 3. Запустить
python window.py