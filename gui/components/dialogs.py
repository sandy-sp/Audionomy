# gui/components/dialogs.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QHBoxLayout
)

class CreateDatasetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Dataset Name:"))
        self.name_input = QLineEdit(self)
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Save Path:"))
        h_layout = QHBoxLayout()
        self.path_input = QLineEdit(self)
        btn_browse = QPushButton("Browse", self)
        btn_browse.clicked.connect(self.browse_folder)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.path_input)
        h_layout.addWidget(btn_browse)
        layout.addLayout(h_layout)

        btn_create = QPushButton("Create Dataset", self)
        btn_create.clicked.connect(self.accept)
        layout.addWidget(btn_create)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Dataset Directory")
        if folder:
            self.path_input.setText(folder)

    def get_data(self):
        return {
            "dataset_name": self.name_input.text(),
            "save_path": self.path_input.text()
        }
