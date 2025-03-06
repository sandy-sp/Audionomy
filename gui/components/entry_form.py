from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from pydub.utils import mediainfo
from datetime import datetime
import shutil, os

class EntryForm(QWidget):
    def __init__(self, dataset_manager, status_bar, refresh_callback):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.status_bar = status_bar
        self.refresh_callback = refresh_callback
        self.audio_file_path = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.song_title = QLineEdit(self)
        self.style_prompt = QLineEdit(self)
        self.exclude_prompt = QLineEdit(self)
        self.duration = QLineEdit(self)
        self.file_format = QLineEdit(self)
        self.model_version = QLineEdit(self)

        btn_upload_audio = QPushButton("Upload Audio")
        btn_upload_audio.clicked.connect(self.upload_audio)

        btn_submit = QPushButton("Submit Entry")
        btn_submit.clicked.connect(self.submit_entry)

        layout.addRow("Song Title", self.song_title)
        layout.addRow("Style Prompt", self.style_prompt)
        layout.addRow("Exclude Style Prompt", self.exclude_prompt)
        layout.addRow("Duration (auto)", self.duration)
        layout.addRow("File Format (auto)", self.file_format)
        layout.addRow("Model Version", self.model_version)
        layout.addRow(btn_upload_audio)
        layout.addRow(btn_submit)

    def upload_audio(self):
        audio_file, _ = QFileDialog.getOpenFileName(self, "Select Audio", filter="Audio (*.mp3 *.wav)")
        if audio_file:
            info = mediainfo(audio_file)
            duration = round(float(info.get('duration', 0)), 2)
            file_format = info.get('format_name', 'unknown')

            self.audio_file_path = audio_file
            self.duration.setText(str(duration))
            self.file_format.setText(file_format)
            self.status_bar.showMessage("Audio metadata auto-filled.", 5000)

    def submit_entry(self):
        if not self.audio_file_path:
            QMessageBox.warning(self, "Warning", "Please upload an audio file.")
            return

        audio_dest = os.path.join(self.dataset_manager.audio_dir, os.path.basename(self.audio_file_path))
        shutil.copy2(self.audio_file_path, audio_dest)

        metadata = {
            "song_title": self.song_title.text(),
            "style_prompt": self.style_prompt.text(),
            "exclude_style_prompt": self.exclude_prompt.text(),
            "audio_file": audio_dest,
            "duration": self.duration.text(),
            "file_format": self.file_format.text(),
            "model_version": self.model_version.text(),
            "generation_date": datetime.now().isoformat(),
        }

        self.dataset_manager.log_entry(metadata)
        QMessageBox.information(self, "Success", "Entry added successfully!")
        self.status_bar.showMessage("Entry logged and audio copied.", 5000)
        self.refresh_callback()
        self.close()
