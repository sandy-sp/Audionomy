# gui/components/dialogs.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QListWidget, QHBoxLayout, QMessageBox, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt
import qtawesome as qta
import os
import json
import pandas as pd


class EnhancedCreateDatasetDialog(QDialog):
    """Dialog for creating a new dataset with template and custom column options."""

    def __init__(self, parent=None, templates_dir="templates"):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.resize(700, 500)
        self.templates_dir = templates_dir
        self.available_templates = self.load_templates()
        self.setup_ui()

    def load_templates(self):
        """Loads available dataset templates from the templates directory."""
        templates = {}
        if os.path.exists(self.templates_dir):
            for file in os.listdir(self.templates_dir):
                if file.endswith('.template'):
                    try:
                        with open(os.path.join(self.templates_dir, file), "r") as f:
                            templates[file.replace(".template", "")] = json.load(f)
                    except:
                        pass
        return templates

    def setup_ui(self):
        """Initializes the UI layout."""
        layout = QVBoxLayout(self)

        # Dataset Name & Location
        form_layout = QVBoxLayout()
        self.dataset_name_input = QLineEdit()
        self.dataset_name_input.setPlaceholderText("Enter dataset name")

        self.dataset_location_input = QLineEdit()
        self.dataset_location_input.setPlaceholderText("Select dataset location")
        browse_btn = QPushButton(qta.icon("fa5s.folder-open"), "")
        browse_btn.clicked.connect(self.browse_location)

        location_layout = QHBoxLayout()
        location_layout.addWidget(self.dataset_location_input)
        location_layout.addWidget(browse_btn)

        form_layout.addWidget(QLabel("Dataset Name:"))
        form_layout.addWidget(self.dataset_name_input)
        form_layout.addWidget(QLabel("Dataset Location:"))
        form_layout.addLayout(location_layout)

        # Dataset Template Selector
        self.use_template_cb = QCheckBox("Use dataset template")
        self.use_template_cb.toggled.connect(self.toggle_template_mode)
        form_layout.addWidget(self.use_template_cb)

        self.template_selector = QComboBox()
        self.template_selector.addItems(["Select a template..."] + list(self.available_templates.keys()))
        self.template_selector.setEnabled(False)
        form_layout.addWidget(self.template_selector)

        # Custom Column Input
        self.custom_columns_list = QListWidget()
        self.column_input = QLineEdit()
        self.column_input.setPlaceholderText("Enter column name")
        add_column_btn = QPushButton(qta.icon("fa5s.plus"), "Add Column")
        add_column_btn.clicked.connect(self.add_column)

        column_layout = QHBoxLayout()
        column_layout.addWidget(self.column_input)
        column_layout.addWidget(add_column_btn)

        form_layout.addWidget(QLabel("Custom Columns:"))
        form_layout.addLayout(column_layout)
        form_layout.addWidget(self.custom_columns_list)

        # Import from CSV
        import_csv_btn = QPushButton(qta.icon("fa5s.file-csv"), "Import Columns from CSV")
        import_csv_btn.clicked.connect(self.import_from_csv)
        form_layout.addWidget(import_csv_btn)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        create_btn = QPushButton(qta.icon("fa5s.plus-circle"), "Create Dataset")
        create_btn.setObjectName("primary-button")
        create_btn.clicked.connect(self.validate_and_accept)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        layout.addLayout(button_layout)

    def toggle_template_mode(self, checked):
        """Enables/disables custom columns when using a template."""
        self.template_selector.setEnabled(checked)
        self.custom_columns_list.setEnabled(not checked)
        self.column_input.setEnabled(not checked)

    def browse_location(self):
        """Opens a file dialog to select dataset location."""
        folder = QFileDialog.getExistingDirectory(self, "Select Dataset Location")
        if folder:
            self.dataset_location_input.setText(folder)

    def add_column(self):
        """Adds a custom column to the list."""
        column_name = self.column_input.text().strip()
        if column_name:
            self.custom_columns_list.addItem(column_name)
            self.column_input.clear()

    def import_from_csv(self):
        """Imports column names from a selected CSV file."""
        file, _ = QFileDialog.getOpenFileName(self, "Select CSV", filter="CSV Files (*.csv)")
        if file:
            try:
                df = pd.read_csv(file, nrows=0)
                self.custom_columns_list.clear()
                self.custom_columns_list.addItems(df.columns.tolist())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import CSV: {str(e)}")

    def validate_and_accept(self):
        """Validates input and accepts the dialog."""
        if not self.dataset_name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter a dataset name.")
            return
        if not self.dataset_location_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please select a dataset location.")
            return

        # Load template columns if selected
        if self.use_template_cb.isChecked():
            selected_template = self.template_selector.currentText()
            if selected_template in self.available_templates:
                columns = self.available_templates[selected_template]["columns"]
            else:
                QMessageBox.warning(self, "Warning", "Please select a valid template.")
                return
        else:
            columns = [self.custom_columns_list.item(i).text() for i in range(self.custom_columns_list.count())]

        if not columns:
            QMessageBox.warning(self, "Warning", "Please add at least one column.")
            return

        self.accept()

    def get_data(self):
        """Returns dataset name, location, and columns."""
        return (
            self.dataset_name_input.text().strip(),
            self.dataset_location_input.text().strip(),
            [self.custom_columns_list.item(i).text() for i in range(self.custom_columns_list.count())]
        )
