from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QListWidget, QMessageBox
)
import pandas as pd

class CreateDatasetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Dataset Name
        self.name_input = QLineEdit(self)
        layout.addWidget(QLabel("Dataset Name"))
        layout.addWidget(self.name_input)

        # Dataset Save Location
        self.path_input = QLineEdit(self)
        browse_btn = QPushButton("Browse Folder")
        browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(QLabel("Dataset Location"))
        layout.addWidget(self.path_input)
        layout.addWidget(browse_btn)

        # Columns List
        layout.addWidget(QLabel("Dataset Columns"))
        self.columns_list = QListWidget(self)
        layout.addWidget(self.columns_list)

        # Import Columns from CSV
        import_btn = QPushButton("Import Columns from CSV")
        import_btn.clicked.connect(self.import_from_csv)
        layout.addWidget(import_btn)

        # Create button
        create_btn = QPushButton("Create Dataset")
        create_btn.clicked.connect(self.validate_and_accept)  # fixed here
        layout.addWidget(create_btn)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.path_input.setText(folder)

    def import_from_csv(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select CSV File", filter="CSV (*.csv)")
        if file:
            try:
                df = pd.read_csv(file, nrows=0)
                self.columns_list.clear()
                self.columns_list.addItems(df.columns.tolist())
            except Exception as e:
                QMessageBox.critical(self, "CSV Error", str(e))

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Missing Name", "Please enter a dataset name.")
            return
        if not self.path_input.text().strip():
            QMessageBox.warning(self, "Missing Path", "Please select a dataset location.")
            return
        if self.columns_list.count() == 0:
            QMessageBox.warning(self, "No Columns", "Please add columns or import from CSV.")
            return
        self.accept()

    def get_data(self):
        return (
            self.name_input.text().strip(),
            self.path_input.text().strip(),
            [self.columns_list.item(i).text() for i in range(self.columns_list.count())]
        )
