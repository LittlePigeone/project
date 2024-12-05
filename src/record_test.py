import sys
import wave
import numpy as np
import sounddevice as sd
from scipy.signal import butter, lfilter
from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QLabel,
    QComboBox,
    QMessageBox,
    QSlider,
)
from PyQt6.QtCore import Qt


def butter_bandpass(lowcut, highcut, fs, order=5):
    """Создаёт параметры полосового фильтра."""
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    return b, a


def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """Применяет полосовой фильтр к данным."""
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)


class AudioRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Recorder")
        self.layout = QVBoxLayout()

        # Выбор устройства
        self.device_label = QLabel("Select Input Device:")
        self.device_selector = QComboBox()
        self.populate_input_devices()

        # Управление фильтрацией
        self.lowcut_label = QLabel("Lowcut Frequency: 20 Hz")
        self.lowcut_slider = QSlider(Qt.Orientation.Horizontal)
        self.lowcut_slider.setRange(20, 1000)  # Частоты от 50 до 1000 Гц
        self.lowcut_slider.setValue(20)
        self.lowcut_slider.valueChanged.connect(self.update_lowcut)

        self.highcut_label = QLabel("Highcut Frequency: 20000 Hz")
        self.highcut_slider = QSlider(Qt.Orientation.Horizontal)
        self.highcut_slider.setRange(20, 20000)  # Частоты от 1 кГц до 8 кГц
        self.highcut_slider.setValue(20000)
        self.highcut_slider.valueChanged.connect(self.update_highcut)

        # Кнопки управления
        self.record_button = QPushButton("Start Recording")
        self.stop_button = QPushButton("Stop Recording")
        self.play_button = QPushButton("Play Recording")
        self.play_button.setEnabled(False)

        self.status_label = QLabel("Press 'Start Recording' to begin.")

        # Сигналы кнопок
        self.record_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.play_button.clicked.connect(self.play_audio)
        self.stop_button.setEnabled(False)

        # Добавление элементов на экран
        self.layout.addWidget(self.device_label)
        self.layout.addWidget(self.device_selector)
        self.layout.addWidget(self.lowcut_label)
        self.layout.addWidget(self.lowcut_slider)
        self.layout.addWidget(self.highcut_label)
        self.layout.addWidget(self.highcut_slider)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.record_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.play_button)
        self.setLayout(self.layout)

        # Параметры записи
        self.recording = False
        self.audio_data = []
        self.selected_device = None
        self.samplerate = 44100
        self.channels = 1
        self.lowcut = 20.0  # Низкая граница частот
        self.highcut = 20000.0  # Высокая граница частот

    def populate_input_devices(self):
        """Заполняет комбобокс списком доступных устройств ввода."""
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                self.device_selector.addItem(f"{device['name']} (ID {i})", i)

    def update_lowcut(self, value):
        self.lowcut = value
        self.lowcut_label.setText(f"Lowcut Frequency: {value} Hz")

    def update_highcut(self, value):
        self.highcut = value
        self.highcut_label.setText(f"Highcut Frequency: {value} Hz")

    def start_recording(self):
        try:
            self.selected_device = self.device_selector.currentData()
            if self.selected_device is None:
                QMessageBox.critical(self, "Error", "Please select a valid input device.")
                return

            self.record_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.play_button.setEnabled(False)
            self.status_label.setText("Recording...")
            self.recording = True
            self.audio_data = []
            self.stream = sd.InputStream(
                device=self.selected_device,
                samplerate=self.samplerate,
                channels=self.channels,
                blocksize=4096,
                callback=self.audio_callback,
                # latency='low'
            )
            self.stream.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start recording: {e}")
            self.reset_ui()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.stream.stop()
            self.stream.close()
            self.save_audio_file("output_filtered.wav")
            self.status_label.setText("Recording saved to 'output_filtered.wav'")
            self.play_button.setEnabled(True)
        self.reset_ui()

    def reset_ui(self):
        """Сбрасывает состояние интерфейса."""
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def __normalize_audio(self, audio_data):
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val  # Приводим к диапазону [-1, 1]
        return (audio_data * 32767).astype(np.int16)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Warning: {status}")

        if self.recording:
            try:
                # Извлекаем первый канал
                audio_data = indata[:, 0]

                # Применяем фильтрацию
                filtered_data = apply_bandpass_filter(audio_data, self.lowcut, self.highcut, self.samplerate)

                # Нормализуем данные
                normalize_audio = self.__normalize_audio(filtered_data)
                self.audio_data.append(normalize_audio)
            except Exception as e:
                print(f"Error in audio callback: {e}")

    def save_audio_file(self, filename):
        try:
            # Объединяем все блоки аудиоданных
            audio_array = np.concatenate(self.audio_data).astype(np.int16)
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16 бит
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_array.tobytes())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def play_audio(self):
        """Проигрывает записанный аудиофайл."""
        if self.audio_data:
            # Объединяем аудиоданные
            audio_array = np.concatenate(self.audio_data).astype(np.int16)
            try:
                sd.play(audio_array, samplerate=self.samplerate)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to play audio: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioRecorder()
    window.show()
    sys.exit(app.exec())
