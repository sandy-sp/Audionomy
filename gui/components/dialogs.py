# gui/components/dialogs.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QFileDialog, QListWidget, QMessageBox, QComboBox, QFrame, QScrollArea,
    QWidget, QCheckBox, QInputDialog
)
from PySide6.QtCore import Qt
import qtawesome as qta
import pandas as pd
import os
import json

class EnhancedCreateDatasetDialog(QDialog):
    def __init__(self, parent=None, templates_dir="templates"):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.resize(700, 600)
        self.templates_dir = templates_dir
        self.available_templates = self.load_available_templates()
        self.setup_ui()
        
    def load_available_templates(self):
        templates = {}
        if os.path.exists(self.templates_dir):
            for file in os.listdir(self.templates_dir):
                if file.endswith('.template'):
                    template_path = os.path.join(self.templates_dir, file)
                    try:
                        with open(template_path, 'r') as f:
                            template_data = json.load(f)
                            templates[file.replace('.template', '')] = template_data
                    except:
                        pass
        return templates

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Create a New Audio Dataset")
        header.setObjectName("dialog-header")
        main_layout.addWidget(header)
        
        # Content area
        content = QScrollArea()
        content.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content.setWidget(content_widget)
        
        # Basic info section
        basic_info = QFrame()
        basic_info.setObjectName("section-frame")
        basic_layout = QVBoxLayout(basic_info)
        basic_layout.addWidget(QLabel("Basic Information"))
        
        # Dataset Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Dataset Name:"))
        self.dataset_name_input = QLineEdit()
        self.dataset_name_input.setPlaceholderText("Enter a descriptive name for your dataset")
        name_layout.addWidget(self.dataset_name_input)
        basic_layout.addLayout(name_layout)
        
        # Dataset Location
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Location:"))
        self.dataset_location_input = QLineEdit()
        self.dataset_location_input.setPlaceholderText("Select where to save your dataset")
        location_layout.addWidget(self.dataset_location_input)
        browse_btn = QPushButton(qta.icon("fa5s.folder-open"), "")
        browse_btn.setToolTip("Browse for folder")
        browse_btn.clicked.connect(self.browse_location)
        location_layout.addWidget(browse_btn)
        basic_layout.addLayout(location_layout)
        
        content_layout.addWidget(basic_info)
        
        # Template section
        template_frame = QFrame()
        template_frame.setObjectName("section-frame")
        template_layout = QVBoxLayout(template_frame)
        template_layout.addWidget(QLabel("Dataset Template"))
        
        # Template selection
        template_choice_layout = QHBoxLayout()
        self.use_template_cb = QCheckBox("Use existing template")
        self.use_template_cb.toggled.connect(self.toggle_template_mode)
        template_choice_layout.addWidget(self.use_template_cb)
        template_choice_layout.addStretch()
        template_layout.addLayout(template_choice_layout)
        
        # Template selector
        self.template_selector = QComboBox()
        self.template_selector.addItems(list(self.available_templates.keys()))
        self.template_selector.setEnabled(False)
        template_layout.addWidget(self.template_selector)
        
        # Custom columns section
        self.custom_columns_frame = QFrame()
        custom_columns_layout = QVBoxLayout(self.custom_columns_frame)
        custom_columns_layout.addWidget(QLabel("Custom Columns"))
        
        # Add column
        add_column_layout = QHBoxLayout()
        self.column_input = QLineEdit()
        self.column_input.setPlaceholderText("Enter column name")
        add_column_btn = QPushButton(qta.icon("fa5s.plus"), "Add")
        add_column_btn.clicked.connect(self.add_column)
        add_column_layout.addWidget(self.column_input)
        add_column_layout.addWidget(add_column_btn)
        custom_columns_layout.addLayout(add_column_layout)
        
        # Columns list
        self.columns_list = QListWidget()
        self.columns_list.setAlternatingRowColors(True)
        self.columns_list.setMinimumHeight(150)
        custom_columns_layout.addWidget(self.columns_list)
        
        # Import from CSV
        import_csv_btn = QPushButton(qta.icon("fa5s.file-csv"), "Import Columns from CSV")
        import_csv_btn.clicked.connect(self.import_from_csv)
        custom_columns_layout.addWidget(import_csv_btn)
        
        template_layout.addWidget(self.custom_columns_frame)
        content_layout.addWidget(template_frame)
        
        # Required columns notice
        notice = QLabel("Note: 'file_format' and 'duration' columns will be automatically added and populated.")
        notice.setObjectName("notice-text")
        content_layout.addWidget(notice)
        
        content_layout.addStretch()
        main_layout.addWidget(content)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        create_btn = QPushButton(qta.icon("fa5s.plus-circle"), "Create Dataset")
        create_btn.setObjectName("primary-button")
        create_btn.clicked.connect(self.validate_and_accept)
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(create_btn)
        main_layout.addLayout(buttons_layout)
        
    def toggle_template_mode(self, checked):
        self.template_selector.setEnabled(checked)
        self.custom_columns_frame.setEnabled(not checked)
        
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
            try:
                df = pd.read_csv(file, nrows=0)
                self.columns_list.clear()
                self.columns_list.addItems(df.columns.tolist())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to import CSV: {str(e)}")

    def validate_and_accept(self):
        if not self.dataset_name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter a dataset name.")
            return
        if not self.dataset_location_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please select a dataset location.")
            return
            
        if self.use_template_cb.isChecked():
            # Using existing template
            if not self.template_selector.currentText():
                QMessageBox.warning(self, "Warning", "Please select a template.")
                return
        else:
            # Using custom columns
            if self.columns_list.count() == 0:
                QMessageBox.warning(self, "Warning", "Please add at least one column.")
                return
                
        self.accept()

    def get_data(self):
        if self.use_template_cb.isChecked():
            template_name = self.template_selector.currentText()
            columns = self.available_templates[template_name]["columns"]
        else:
            columns = [self.columns_list.item(i).text() for i in range(self.columns_list.count())]
            
        # Ensure required columns exist
        if "file_format" not in columns:
            columns.append("file_format")
        if "duration" not in columns:
            columns.append("duration")
            
        return (
            self.dataset_name_input.text().strip(),
            self.dataset_location_input.text().strip(),
            columns
        )
