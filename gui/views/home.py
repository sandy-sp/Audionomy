# gui/views/home.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
)
from components.dialogs import CreateDatasetDialog
import os

class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        label = QLabel("🎵 Welcome to Audionomy!", self)
        layout.addWidget(label)

        btn_create_dataset = QPushButton("📁 Create New Dataset", self)
        btn_create_dataset.clicked.connect(self.create_dataset)
        layout.addWidget(btn_create_dataset)

        btn_open_dataset = QPushButton("📂 Open Existing Dataset", self)
        btn_open_dataset.clicked.connect(self.open_dataset)
        layout.addWidget(btn_open_dataset)

        self.setLayout(layout)

    def create_dataset(self):
        dialog = CreateDatasetDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            dataset_name = data["dataset_name"]
            save_path = data["save_path"]

            if dataset_name and save_path:
                full_path = os.path.join(save_path, dataset_name)
                try:
                    os.makedirs(full_path, exist_ok=True)
                    QMessageBox.information(
                        self, "Success", f"Dataset '{dataset_name}' created at {save_path}"
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

    def open_dataset(self):
        dataset_path = QFileDialog.getExistingDirectory(
            self, "Select Dataset Directory", os.getcwd()
        )
        if dataset_path:
            QMessageBox.information(self, "Dataset Selected", f"Opened dataset at: {dataset_path}")
