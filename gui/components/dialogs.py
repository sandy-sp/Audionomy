from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QHBoxLayout

class CreateDatasetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.name_input = QLineEdit(self)
        layout.addWidget(QLabel("Dataset Name"))
        layout.addWidget(self.name_input)

        self.path_input = QLineEdit(self)
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_folder)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(btn_browse)

        layout.addWidget(QLabel("Save Location"))
        layout.addLayout(path_layout)

        btn_create = QPushButton("Create Dataset")
        btn_create.clicked.connect(self.accept)
        layout.addWidget(btn_create)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.path_input.setText(folder)

    def get_data(self):
        return {
            "dataset_name": self.name_input.text(),
            "save_path": self.path_input.text()
        }
