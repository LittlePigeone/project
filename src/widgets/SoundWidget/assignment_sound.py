import pygame
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QDialog
from pathlib import Path

from database.main import DataBase


class AssignmentWindow(QDialog):
    def __init__(self, parent, sounds_dir, database: DataBase):
        super().__init__(parent)
        self.parent = parent
        self.sounds_dir = Path(sounds_dir)
        self.sound_files = list(self.sounds_dir.glob("*.wav"))
        self.key_bindings = {}
        self.database = database
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Привязка звуков к клавишам")
        layout = QVBoxLayout()

        # Создаём таблицу
        self.table = QTableWidget(len(self.sound_files), 2)
        self.table.setHorizontalHeaderLabels(["Файл звука", "Привязка клавиши"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.updateTable()

        self.table.cellClicked.connect(self.onCellClicked)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.resize(400, 300)

    def updateTable(self):
        """Обновляет таблицу с файлами и привязками клавиш."""
        for row, sound_file in enumerate(self.sound_files):
            # Имя файла
            self.table.setItem(row, 0, QTableWidgetItem(sound_file.name))

            # Привязка клавиши
            current_key = next((key for key, val in self.parent.binding.items() if val.get('name') == sound_file.name), 'Не назначено')
            if current_key != 'Не назначено':
                current_key = chr(int(current_key))
            key_name = self.key_bindings.get(sound_file, current_key)
            self.table.setItem(row, 1, QTableWidgetItem(key_name))

    def onCellClicked(self, row, column):
        """Обрабатывает нажатие на ячейку таблицы."""
        if column == 1:  # Разрешаем привязку только в правой колонке
            sound_file = self.sound_files[row]
            self.bind_key_to_sound(sound_file)

    def bind_key_to_sound(self, sound_file):
        """Привязывает клавишу к звуку."""
        self.setFocus()  # Ставим фокус на окно, чтобы получить событие keyPressEvent
        self.current_sound = sound_file

    def keyPressEvent(self, event):
        """Обрабатывает нажатие клавиши для привязки."""
        if hasattr(self, 'current_sound') and self.current_sound:
            key = event.key()
            self.key_bindings[self.current_sound] = chr(key)  # Привязываем клавишу
            sound_path = self.sounds_dir / self.current_sound.name  # Получаем путь к файлу

            if self.parent.binding.get(key, False):
                id = self.parent.binding[key]['id']
                self.database.update({
                    'id': id,
                    'key': key,
                })
            else:
                id = self.database.create({
                    'path': str(Path('sounds') / self.current_sound.name),
                    'name': self.current_sound.name,
                    'key': key,
                })

            self.parent.binding[key] = {
                'id': id,
                'name': self.current_sound.name,
                'sound': pygame.mixer.Sound(str(sound_path)),
                'key': key,
            }

            self.current_sound = None  # Сбрасываем текущее состояние
            self.updateTable()  # Обновляем таблицу с привязками
            self.parent.updateSoundButton()
        else:
            print("Нет выбранного звука для привязки.")
