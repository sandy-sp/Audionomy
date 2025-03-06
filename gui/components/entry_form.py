# gui/components/entry_form.py

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QListWidget, QVBoxLayout, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt
from scripts.audio_processing import AudioProcessor
import os
import shutil


class EntryForm(QWidget):
    """Dialog for adding metadata entries for audio files."""

    def __init__(self, dataset_manager, status_bar, refresh_callback):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.status_bar = status_bar
        self.refresh_callback = refresh_callback
        self.audio_processor = AudioProcessor(normalize=True, target_format="wav")
        self.audio_files = []
        self.setup_ui()

    def setup_ui(self):
        """Initializes the UI layout."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Add Audio Entry")
        header.setObjectName("page-header")
        layout.addWidget(header)

        # File Selection
        file_layout = QHBoxLayout()
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)

        btn_upload_audio = QPushButton("📂 Select Audio Files")
        btn_upload_audio.clicked.connect(self.upload_audio)
        file_layout.addWidget(btn_upload_audio)
        layout.addLayout(file_layout)

        # Metadata Form
        form_layout = QFormLayout()
        self.song_title = QLineEdit()
        self.style_prompt = QLineEdit()
        self.exclude_prompt = QLineEdit()
        self.duration = QLineEdit()
        self.file_format = QLineEdit()
        self.model_version = QLineEdit()

        self.duration.setReadOnly(True)
        self.file_format.setReadOnly(True)

        form_layout.addRow("Song Title", self.song_title)
        form_layout.addRow("Style Prompt", self.style_prompt)
        form_layout.addRow("Exclude Style Prompt", self.exclude_prompt)
        form_layout.addRow("Duration (Auto-filled)", self.duration)
        form_layout.addRow("File Format (Auto-filled)", self.file_format)
        form_layout.addRow("Model Version", self.model_version)

        layout.addLayout(form_layout)

        # Buttons
        btn_submit = QPushButton("✅ Submit Entry")
        btn_submit.clicked.connect(self.submit_entries)

        btn_clear = QPushButton("❌ Clear Form")
        btn_clear.clicked.connect(self.clear_form)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_submit)
        layout.addLayout(btn_layout)

    def upload_audio(self):
        """Opens file dialog for selecting audio files."""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Audio Files", filter="Audio Files (*.mp3 *.wav *.flac *.ogg)")
        if files:
            self.audio_files.extend(files)
            self.update_file_list()
            self.auto_fill_metadata()

    def update_file_list(self):
        """Updates the file list UI component."""
        self.file_list.clear()
        for file in self.audio_files:
            self.file_list.addItem(os.path.basename(file))

    def auto_fill_metadata(self):
        """Auto-fills metadata for the first selected file."""
        if self.audio_files:
            metadata, _ = self.audio_processor.process_audio_file(self.audio_files[0])
            self.duration.setText(str(metadata.get("duration", "")))
            self.file_format.setText(metadata.get("file_format", "").upper())

    def clear_form(self):
        """Clears all input fields and resets the form."""
        self.song_title.clear()
        self.style_prompt.clear()
        self.exclude_prompt.clear()
        self.duration.clear()
        self.file_format.clear()
        self.model_version.clear()
        self.file_list.clear()
        self.audio_files = []

    def submit_entries(self):
        """Submits multiple audio entries with metadata."""
        if not self.audio_files:
            QMessageBox.warning(self, "Warning", "No audio files selected!")
            return

        added_count = 0
        for file in self.audio_files:
            metadata, converted_path = self.audio_processor.process_audio_file(file, output_dir=self.dataset_manager.audio_dir)

            # Ensure the file is copied to the dataset directory
            audio_dest = os.path.join(self.dataset_manager.audio_dir, os.path.basename(converted_path))
            shutil.copy2(converted_path, audio_dest)

            # Create metadata entry
            entry = {
                "song_title": self.song_title.text() or os.path.splitext(os.path.basename(file))[0],
                "style_prompt": self.style_prompt.text(),
                "exclude_style_prompt": self.exclude_prompt.text(),
                "audio_file": os.path.basename(audio_dest),
                "duration": metadata.get("duration", ""),
                "file_format": metadata.get("file_format", ""),
                "model_version": self.model_version.text(),
                "generation_date": metadata.get("generation_date", ""),
            }

            self.dataset_manager.log_entry(entry)
            added_count += 1

        self.status_bar.showMessage(f"{added_count} audio entries added.", 5000)
        self.refresh_callback()
        self.close()
