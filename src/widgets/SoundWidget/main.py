import wave
from datetime import datetime

import pygame
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from database.main import DataBase
from widgets.SoundWidget.assignment_sound import AssignmentWindow


class SoundWidget(QWidget):
    def __init__(self, base_dir):
        super().__init__()

        self.base_dir = base_dir
        self.sounds_path = self.base_dir / 'sounds'
        self.is_recording = False
        self.recorded_notes = []
        self.database = DataBase(base_dir, 'db.sqlite3')

        self.__initSounds()
        self.__initKeys()
        self.__initUI()

    def __initUI(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        h_layout = QHBoxLayout()
        layout = QVBoxLayout()
        up_layout = QVBoxLayout()
        self.down_layout = QVBoxLayout()

        self.record_button = QPushButton('Начать запись')
        self.stop_record_button = QPushButton('Остановить запись')
        assign_button = QPushButton('Настроить клавиши')

        assign_button.clicked.connect(self.openAssignmentWindow)
        self.record_button.clicked.connect(self.__start_recording)
        self.stop_record_button.clicked.connect(self.__stop_recording)

        h_layout.addWidget(self.record_button)
        h_layout.addWidget(self.stop_record_button)

        up_layout.addLayout(h_layout)
        up_layout.addWidget(assign_button)

        layout.addLayout(up_layout)
        layout.addLayout(self.down_layout)
        self.setLayout(layout)

        self.__initSoundButton()

    def __initSoundButton(self):
        for key in self.binding.keys():
            button = QPushButton(f"Кнопка {chr(Qt.Key(int(key)))}")
            button.clicked.connect(lambda _, note=key: self.play_sound(note))
            self.down_layout.addWidget(button)

    def __clearSoundButton(self):
        while self.down_layout.count():
            child = self.down_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def updateSoundButton(self):
        self.__clearSoundButton()
        self.__initKeys()
        self.__initSoundButton()

    def __initKeys(self):
        sounds_bind = self.database.get()

        self.binding = {}
        for sound in sounds_bind:
            self.binding[int(sound[3])] = {
                'id': sound[0],
                'name': sound[2],
                'sound': pygame.mixer.Sound(str(self.base_dir / sound[1]))
            }

    def __initSounds(self):
        pygame.mixer.init()

    def keyPressEvent(self, event):
        key = event.key()
        if key in self.binding.keys():
            self.play_sound(key)

            if self.is_recording:
                self.recorded_notes.append(key)

    def play_sound(self, note):
        self.binding[note]['sound'].play()

    def openAssignmentWindow(self):
        self.assignment_window = AssignmentWindow(self, str(self.base_dir / 'sounds'), self.database)
        self.assignment_window.show()

    def __start_recording(self):
        self.record_button.setEnabled(False)
        self.stop_record_button.setEnabled(True)
        print('-> Идёт запись...')
        self.is_recording = True
        self.recorded_notes.clear()

    def __stop_recording(self):
        if not self.is_recording:
            return
        self.record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        print("Запись завершена!")
        self.is_recording = False
        self.__save_recorded_melody()

    def __save_recorded_melody(self):
        filename = f"{datetime.now()}.wav".replace(' ', '_').replace(':', '_')
        filepath = self.base_dir / 'sounds' / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(filepath), 'wb') as file:
            params = (1, 4, 44100, 0, 'NONE', 'not compressed')
            file.setparams(params)

            for note in self.recorded_notes:
                data = self.binding[note]['sound'].get_raw()
                file.writeframes(data)

        print(f"Мелодия сохранена в файл: {filepath}")


AudioWidget = SoundWidget