from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QFileDialog, QListWidget, QMessageBox, QHBoxLayout
)
import pandas as pd

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
        browse_btn = QPushButton("Browse Folder")
        browse_btn.clicked.connect(self.browse_folder)

        layout.addWidget(QLabel("Dataset Location"))
        layout.addWidget(self.path_input)
        layout.addWidget(browse_btn)

        layout.addWidget(QLabel("Dataset Columns"))
        self.columns_list = QListWidget(self)
        layout.addWidget(self.columns_list)

        # Define import_btn clearly (previously missing)
        import_btn = QPushButton("Import Columns from CSV")
        import_btn.clicked.connect(self.import_from_csv)
        layout.addWidget(import_btn)

        create_btn = QPushButton("Create Dataset")
        create_btn.clicked.connect(self.validate_and_accept)
        layout.addWidget(create_btn)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Dataset Location")
        if folder:
            self.path_input.setText(folder)

    def import_from_csv(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select CSV File", filter="CSV Files (*.csv)")
        if file:
            try:
                df = pd.read_csv(file, nrows=0)
                self.columns_list.clear()
                self.columns_list.addItems(df.columns.tolist())
            except Exception as e:
                QMessageBox.critical(self, "CSV Error", f"Failed to load CSV: {e}")

    def validate(self):
        if not self.name_input.text() or not self.path_input.text() or self.columns_list.count() == 0:
            QMessageBox.warning(self, "Incomplete Data", "Please fill all fields and add columns.")
            return False
        return True

    def validate(self):
        if self.validate():
            super().accept()

    def get_data(self):
        return (
            self.name_input.text(),
            self.path_input.text(),
            [self.columns_list.item(i).text() for i in range(self.columns_list.count())]
        )
