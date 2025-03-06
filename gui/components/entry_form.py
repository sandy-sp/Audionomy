# gui/components/entry_form.py

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QListWidget, QVBoxLayout, QLabel, QHBoxLayout, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
import os
import shutil
from scripts.audio_processing import AudioProcessor


class MetadataProcessingWorker(QThread):
    """Handles batch metadata entry processing in a separate thread."""

    progress_updated = Signal(int)
    processing_complete = Signal(int)

    def __init__(self, dataset_manager, file_paths, output_dir):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.file_paths = file_paths
        self.output_dir = output_dir
        self.processor = AudioProcessor(normalize=True, target_format="wav")

    def run(self):
        """Processes multiple metadata entries in batch mode."""
        total_files = len(self.file_paths)
        added_count = 0

        for i, file_path in enumerate(self.file_paths):
            try:
                metadata, converted_path = self.processor.process_audio_file(file_path, self.output_dir)

                # Copy converted file to dataset directory
                audio_dest = os.path.join(self.output_dir, os.path.basename(converted_path))
                shutil.copy2(converted_path, audio_dest)

                # Create metadata entry
                entry = {
                    "song_title": os.path.splitext(os.path.basename(file_path))[0],
                    "audio_file": os.path.basename(audio_dest),
                    "duration": metadata.get("duration", ""),
                    "file_format": metadata.get("file_format", ""),
                    "generation_date": metadata.get("generation_date", ""),
                }
                self.dataset_manager.log_entry(entry)

                added_count += 1
                progress = int(((i + 1) / total_files) * 100)
                self.progress_updated.emit(progress)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        self.processing_complete.emit(added_count)


class EntryForm(QWidget):
    """Dialog for adding metadata entries for audio files."""

    def __init__(self, dataset_manager, status_bar, refresh_callback):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.status_bar = status_bar
        self.refresh_callback = refresh_callback
        self.audio_files = []
        self.processing_worker = None
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

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

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
            metadata, _ = AudioProcessor().process_audio_file(self.audio_files[0])
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
        """Starts the threaded batch processing of metadata entries."""
        if not self.audio_files:
            QMessageBox.warning(self, "Warning", "No audio files selected!")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.processing_worker = MetadataProcessingWorker(self.dataset_manager, self.audio_files, self.dataset_manager.audio_dir)
        self.processing_worker.progress_updated.connect(self.progress_bar.setValue)
        self.processing_worker.processing_complete.connect(self.on_processing_complete)
        self.processing_worker.start()

    def on_processing_complete(self, added_count):
        """Handles completion of the batch processing task."""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"{added_count} audio entries added.", 5000)
        self.refresh_callback()
        self.close()
