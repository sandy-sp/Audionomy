from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt  # ✅ Fix: added missing import
from components.dialogs import CreateDatasetDialog
from scripts.dataset_manager import DatasetManager
import os

class HomeView(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar
        self.dataset_manager = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("<h2>🎧 Audionomy Dataset Manager</h2>"))

        btn_create = QPushButton("📁 Create New Dataset")
        btn_create.clicked.connect(self.create_dataset)
        layout.addWidget(btn_create)

        btn_open = QPushButton("📂 Open Existing Dataset")
        btn_open.clicked.connect(self.open_dataset)
        layout.addWidget(btn_open)

    def create_dataset(self):
        dialog = CreateDatasetDialog(self)
        if dialog.exec():
            dataset_name, dataset_path, columns = dialog.get_data()

            if not dataset_name or not dataset_path or not columns:
                QMessageBox.warning(self, "Error", "Missing dataset details or columns.")
                return

            full_path = os.path.join(dataset_path, dataset_name)
            os.makedirs(full_path, exist_ok=True)

            self.dataset_manager = DatasetManager(
                full_path, create_new=True, columns=columns
            )
            self.dataset_manager.init_metadata()

            QMessageBox.information(self, "Success", f"Dataset '{dataset_name}' created successfully!")
            self.status_bar.showMessage(f"Dataset '{dataset_name}' created.", 5000)

    def open_dataset(self):
        path = QFileDialog.getExistingDirectory(self, "Open Dataset")
        if path:
            template_files = [f for f in os.listdir(path) if f.endswith(".template")]
            if not template_files:
                QMessageBox.warning(self, "Invalid Dataset", "No Audionomy dataset (.template) found!")
                return

            self.dataset_manager = DatasetManager(path)
            QMessageBox.information(self, "Loaded", f"Dataset loaded from {path}")
            self.status_bar.showMessage(f"Dataset loaded from {path}", 5000)
