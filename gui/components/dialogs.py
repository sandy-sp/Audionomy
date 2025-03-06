from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QFileDialog, QListWidget, QHBoxLayout, QMessageBox
)
import pandas as pd

class CreateDatasetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Dataset Name Input
        self.dataset_name_input = QLineEdit()
        layout.addWidget(QLabel("Dataset Name"))
        layout.addWidget(self.dataset_name_input)

        # Dataset Location Input
        self.dataset_location_input = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_location)
        layout.addWidget(QLabel("Dataset Location"))
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(self.dataset_location_input)
        loc_layout.addWidget(browse_btn)
        layout.addLayout(loc_layout)

        # Columns input (manual)
        column_input_layout = QHBoxLayout()
        self.column_input = QLineEdit()
        add_column_btn = QPushButton("Add Column")
        add_column_btn.clicked.connect(self.add_column)
        column_input_layout.addWidget(self.column_input)
        column_input_layout.addWidget(add_column_btn)
        layout.addWidget(QLabel("Dataset Columns"))
        layout.addLayout(column_input_layout)

        # Columns List
        self.columns_list = QListWidget()
        layout.addWidget(self.columns_list)

        # Import from CSV button
        import_csv_btn = QPushButton("Import Columns from CSV")
        import_csv_btn.clicked.connect(self.import_from_csv)
        layout.addWidget(import_csv_btn)

        # Create dataset button
        create_btn = QPushButton("Create Dataset")
        create_btn.clicked.connect(self.validate_and_accept)
        layout.addWidget(create_btn)

        self.setLayout(layout)

    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Location")
        if folder:
            self.dataset_location_input.setText(folder)

    def add_column(self):
        col_name = self.column_input.text().strip()
        if col_name:
            self.columns_list.addItem(col_name)
            self.column_input.clear()

    def import_from_csv(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select CSV", filter="CSV Files (*.csv)")
        if file:
            df = pd.read_csv(file, nrows=0)
            self.columns_list.clear()
            self.columns_list.addItems(df.columns.tolist())

    def validate_and_accept(self):
        if not self.dataset_name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter a dataset name.")
            return
        if not self.dataset_location_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please select a dataset location.")
            return
        if self.columns_list.count() == 0:
            QMessageBox.warning(self, "Warning", "Please add at least one column.")
            return
        self.accept()

    def get_data(self):
        columns = [self.columns_list.item(i).text() for i in range(self.columns_list.count())]
        return (
            self.dataset_name_input.text().strip(),
            self.dataset_location_input.text().strip(),
            columns
        )
