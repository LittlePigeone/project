import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel

from style import style
from widgets.RecordWidget.main import RecordWidget
from widgets.SoundWidget.main import AudioWidget
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class MediaTools(QMainWindow):
    def __init__(self, soundWidget, recordWidget):
        super().__init__()

        self.soundWidget = soundWidget(BASE_DIR)
        self.recordWidget = recordWidget(str(BASE_DIR / 'sounds'))

        self.__initUI()

    def __initUI(self):
        self.setFixedSize(400, 600)

        tab_widget = QTabWidget()

        tab_widget.addTab(self.soundWidget, "Звуки")
        tab_widget.addTab(self.recordWidget, "Запись")

        self.setCentralWidget(tab_widget)

        self.setStyleSheet(style)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MediaTools(AudioWidget, RecordWidget)
    window.show()
    sys.exit(app.exec())
