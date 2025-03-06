from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog

class CreateDatasetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.dataset_name = QLineEdit(self)
        self.dataset_path = QLineEdit(self)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Dataset Name"))
        layout.addWidget(self.dataset_name)
        layout.addWidget(QLabel("Dataset Location"))
        layout.addWidget(self.dataset_path)

        btn_browse = QPushButton("Browse", self)
        btn_browse.clicked.connect(self.browse_folder)
        layout.addWidget(btn_browse)

        btn_create = QPushButton("Create")
        btn_create.clicked.connect(self.accept)
        layout.addWidget(btn_create)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Dataset Location")
        if folder:
            self.dataset_path.setText(folder)

    def get_data(self):
        return self.dataset_name.text(), self.dataset_path.text()
