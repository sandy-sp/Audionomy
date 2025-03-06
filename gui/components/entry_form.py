# gui/components/entry_form.py
from PySide6.QtWidgets import (QWidget, QFormLayout, QLineEdit, QPushButton,
                               QFileDialog, QMessageBox)

class EntryForm(QWidget):
    def __init__(self, dataset_manager, status_bar):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.status_bar = status_bar
        self.audio_file_1 = ""
        self.audio_file_2 = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.song_title = QLineEdit(self)
        self.style_prompt = QLineEdit(self)
        self.exclude_prompt = QLineEdit(self)
        self.file_format = QLineEdit(self)
        self.duration = QLineEdit(self)
        self.model_version = QLineEdit(self)
        self.lyrics = QLineEdit(self)
        self.persona = QLineEdit(self)

        btn_audio1 = QPushButton("Upload Audio File 1")
        btn_audio1.clicked.connect(self.upload_audio1)

        btn_audio2 = QPushButton("Upload Audio File 2")
        btn_audio2.clicked.connect(self.upload_audio2)

        btn_submit = QPushButton("Submit Entry")
        btn_submit.clicked.connect(self.submit_entry)

        layout.addRow("Song Title", self.song_title)
        layout.addRow("Style Prompt", self.style_prompt)
        layout.addRow("Exclude Style Prompt", self.exclude_prompt)
        layout.addRow("File Format", self.file_format)
        layout.addRow("Duration (s)", self.duration)
        layout.addRow("Model Version", self.model_version)
        layout.addRow("Lyrics", self.lyrics)
        layout.addRow("Persona", self.persona)
        layout.addRow(btn_audio1, btn_audio2)
        layout.addRow(btn_submit)

    def upload_audio1(self):
        file, _ = QFileDialog.getOpenFileName(self, "Upload Audio File 1")
        if file:
            self.audio_file_1 = file
            self.status_bar.showMessage(f"Selected: {file}", 5000)

    def upload_audio2(self):
        file, _ = QFileDialog.getOpenFileName(self, "Upload Audio File 2")
        if file:
            self.audio_file_2 = file
            self.status_bar.showMessage(f"Selected: {file}", 5000)

    def submit_entry(self):
        metadata = {
            "song_title": self.song_title.text(),
            "style_prompt": self.style_prompt.text(),
            "exclude_style_prompt": self.exclude_prompt.text(),
            "audio_file_1": self.audio_file_1,
            "audio_file_2": self.audio_file_2,
            "file_format": self.file_format.text(),
            "duration": self.duration.text(),
            "model_version": self.model_version.text(),
            "lyrics": self.lyrics.text(),
            "persona": self.persona.text(),
            "uploaded_sample": ""
        }
        self.dataset_manager.log_entry(metadata)
        QMessageBox.information(self, "Success", "Entry added successfully!")
        self.status_bar.showMessage("Audio entry logged successfully!", 5000)
