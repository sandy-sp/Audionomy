from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox
from pydub.utils import mediainfo

class EntryForm(QWidget):
    def __init__(self, dataset_manager, status_bar):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.status_bar = status_bar
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

        btn_upload_audio = QPushButton("Upload Audio File")
        btn_upload_audio.clicked.connect(self.upload_audio)

        btn_submit = QPushButton("Submit Entry")
        btn_submit.clicked.connect(self.submit_entry)

        layout.addRow("Song Title", self.song_title)
        layout.addRow("Style Prompt", self.style_prompt)
        layout.addRow("Exclude Style Prompt", self.exclude_prompt)
        layout.addRow("Duration (auto-filled)", self.duration)
        layout.addRow("File Format (auto-filled)", self.file_format)
        layout.addRow("Model Version", self.model_version)
        layout.addRow(btn_upload_audio)
        layout.addRow(btn_submit := QPushButton("Submit Entry"))

        btn_submit.clicked.connect(self.submit_entry)

    def upload_audio(self):
        audio_file, _ = QFileDialog.getOpenFileName(self, "Upload Audio", filter="Audio Files (*.mp3 *.wav)")
        if audio_file:
            info = mediainfo(audio_file)
            duration = float(info.get('duration', 0))
            file_format = info.get('format_name', 'unknown')

            self.audio_file_path = audio_file
            self.duration.setText(str(duration))
            self.file_format.setText(file_format)

    def submit_entry(self):
        metadata = {
            "song_title": self.song_title.text(),
            "style_prompt": self.style_prompt.text(),
            "exclude_style_prompt": self.exclude_prompt.text(),
            "audio_file_1": self.audio_file_path,
            "duration": self.duration.text(),
            "file_format": self.file_format.text(),
            "model_version": self.model_version.text(),
            "generation_date": datetime.now().isoformat(),
        }

        self.dataset_manager.log_entry(metadata)
        QMessageBox.information(self, "Success", "Entry successfully added!")
        self.status_bar.showMessage("Entry logged successfully.", 5000)
