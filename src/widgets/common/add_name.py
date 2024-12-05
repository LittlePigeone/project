from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton

from style import style


class AddName(QWidget):
    name_saved = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Имя файла')
        layout = QVBoxLayout()

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText('Введите имя файла')
        layout.addWidget(self.name_input)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton('Сохранить')
        self.cancel_button = QPushButton('Отмена')

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.save_button.clicked.connect(self.save_name)
        self.cancel_button.clicked.connect(self.emit_cancel)

        self.setStyleSheet(style)

    def save_name(self):
        file_name = self.name_input.text().strip()
        if file_name:
            self.name_saved.emit({'file': file_name, 'cancel': False})
            self.close()

    def emit_cancel(self):
        self.name_saved.emit({'filename': '', 'cancel': True})
        self.close()