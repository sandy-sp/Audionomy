# gui/views/export_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFrame, QGridLayout, QCheckBox, QFileDialog, QMessageBox, QLineEdit,
    QFormLayout, QTabWidget, QStackedWidget
)
from PySide6.QtCore import Qt
import qtawesome as qta
import os
import pandas as pd
import json
import shutil

class ExportView(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.setup_ui()
        self.load_available_datasets()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Export Dataset")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Dataset selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Dataset:"))
        self.dataset_selector = QComboBox()
        self.dataset_selector.currentIndexChanged.connect(self.load_dataset)
        selector_layout.addWidget(self.dataset_selector)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Export options tabs
        self.tabs = QTabWidget()
        
        # Local export tab
        self.local_tab = QWidget()
        local_layout = QVBoxLayout(self.local_tab)
        
        # Export format
        format_frame = QFrame()
        format_frame.setObjectName("section-frame")
        format_layout = QVBoxLayout(format_frame)
        format_layout.addWidget(QLabel("Export Format"))
        
        self.format_selector = QComboBox()
        self.format_selector.addItems(["CSV", "JSON", "ZIP Archive", "Hugging Face Dataset"])
        self.format_selector.currentIndexChanged.connect(self.update_format_options)
        format_layout.addWidget(self.format_selector)
        
        local_layout.addWidget(format_frame)
        
        # Export options
        options_frame = QFrame()
        options_frame.setObjectName("section-frame")
        options_layout = QVBoxLayout(options_frame)
        options_layout.addWidget(QLabel("Export Options"))
        
        form_layout = QFormLayout()
        
        self.include_audio_cb = QCheckBox("Include audio files")
        self.include_audio_cb.setChecked(True)
        form_layout.addRow("", self.include_audio_cb)
        
        self.normalize_audio_cb = QCheckBox("Normalize audio files")
        form_layout.addRow("", self.normalize_audio_cb)
        
        self.destination_input = QLineEdit()
        browse_btn = QPushButton(qta.icon("fa5s.folder-open"), "")
        browse_btn.clicked.connect(self.browse_destination)
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(self.destination_input)
        dest_layout.addWidget(browse_btn)
        form_layout.addRow("Destination:", dest_layout)
        
        options_layout.addLayout(form_layout)
        local_layout.addWidget(options_frame)
        
        # Format specific options
        self.format_options_stack = QStackedWidget()
        
        # CSV options
        csv_widget = QWidget()
        csv_layout = QFormLayout(csv_widget)
        self.csv_delimiter = QComboBox()
        self.csv_delimiter.addItems([",", ";", "\\t", "|"])
        csv_layout.addRow("Delimiter:", self.csv_delimiter)
        self.csv_header = QCheckBox("Include header")
        self.csv_header.setChecked(True)
        csv_layout.addRow("", self.csv_header)
        self.format_options_stack.addWidget(csv_widget)
        
        # JSON options
        json_widget = QWidget()
        json_layout = QFormLayout(json_widget)
        self.json_pretty = QCheckBox("Pretty print (indented)")
        self.json_pretty.setChecked(True)
        json_layout.addRow("", self.json_pretty)
        self.format_options_stack.addWidget(json_widget)
        
        # ZIP options
        zip_widget = QWidget()
        zip_layout = QFormLayout(zip_widget)
        self.zip_compression = QComboBox()
        self.zip_compression.addItems(["Standard", "Maximum", "Fast"])
        zip_layout.addRow("Compression:", self.zip_compression)
        self.format_options_stack.addWidget(zip_widget)
        
        # Hugging Face options
        hf_widget = QWidget()
        hf_layout = QFormLayout(hf_widget)
        self.hf_dataset_name = QLineEdit()
        hf_layout.addRow("Dataset Name:", self.hf_dataset_name)
        self.hf_private = QCheckBox("Private dataset")
        hf_layout.addRow("", self.hf_private)
        self.format_options_stack.addWidget(hf_widget)
        
        local_layout.addWidget(self.format_options_stack)
        
        # Cloud export tab
        self.cloud_tab = QWidget()
        cloud_layout = QVBoxLayout(self.cloud_tab)
        
        # Service selection
        service_frame = QFrame()
        service_frame.setObjectName("section-frame")
        service_layout = QVBoxLayout(service_frame)
        service_layout.addWidget(QLabel("Cloud Service"))
        
        self.service_selector = QComboBox()
        self.service_selector.addItems(["Hugging Face", "GitHub", "Kaggle"])
        self.service_selector.currentIndexChanged.connect(self.update_service_options)
        service_layout.addWidget(self.service_selector)
        
        cloud_layout.addWidget(service_frame)
        
        # Authentication
        auth_frame = QFrame()
        auth_frame.setObjectName("section-frame")
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.addWidget(QLabel("Authentication"))
        
        self.auth_stack = QStackedWidget()
        
        # Hugging Face auth
        hf_auth = QWidget()
        hf_auth_layout = QFormLayout(hf_auth)
        self.hf_token = QLineEdit()
        self.hf_token.setEchoMode(QLineEdit.Password)
        hf_auth_layout.addRow("API Token:", self.hf_token)
        self.auth_stack.addWidget(hf_auth)
        
        # GitHub auth
        github_auth = QWidget()
        github_auth_layout = QFormLayout(github_auth)
        self.github_token = QLineEdit()
        self.github_token.setEchoMode(QLineEdit.Password)
        github_auth_layout.addRow("Personal Access Token:", self.github_token)
        self.github_username = QLineEdit()
        github_auth_layout.addRow("Username:", self.github_username)
        self.auth_stack.addWidget(github_auth)
        
        # Kaggle auth
        kaggle_auth = QWidget()
        kaggle_auth_layout = QFormLayout(kaggle_auth)
        self.kaggle_username = QLineEdit()
        kaggle_auth_layout.addRow("Username:", self.kaggle_username)
        self.kaggle_key = QLineEdit()
        self.kaggle_key.setEchoMode(QLineEdit.Password)
        kaggle_auth_layout.addRow("API Key:", self.kaggle_key)
        self.auth_stack.addWidget(kaggle_auth)
        
        auth_layout.addWidget(self.auth_stack)
        cloud_layout.addWidget(auth_frame)
        
        # Repository info
        repo_frame = QFrame()
        repo_frame.setObjectName("section-frame")
        repo_layout = QVBoxLayout(repo_frame)
        repo_layout.addWidget(QLabel("Repository Information"))
        
        self.repo_stack = QStackedWidget()
        
        # Hugging Face repo
        hf_repo = QWidget()
        hf_repo_layout = QFormLayout(hf_repo)
        self.hf_repo_name = QLineEdit()
        hf_repo_layout.addRow("Repository Name:", self.hf_repo_name)
        self.hf_repo_private = QCheckBox("Private repository")
        hf_repo_layout.addRow("", self.hf_repo_private)
        self.repo_stack.addWidget(hf_repo)
        
        # GitHub repo
        github_repo = QWidget()
        github_repo_layout = QFormLayout(github_repo)
        self.github_repo_name = QLineEdit()
        github_repo_layout.addRow("Repository Name:", self.github_repo_name)
        self.github_repo_private = QCheckBox("Private repository")
        github_repo_layout.addRow("", self.github_repo_private)
        self.repo_stack.addWidget(github_repo)
        
        # Kaggle dataset
        kaggle_dataset = QWidget()
        kaggle_dataset_layout = QFormLayout(kaggle_dataset)
        self.kaggle_dataset_title = QLineEdit()
        kaggle_dataset_layout.addRow("Dataset Title:", self.kaggle_dataset_title)
        self.kaggle_dataset_public = QCheckBox("Public dataset")
        kaggle_dataset_layout.addRow("", self.kaggle_dataset_public)
        self.repo_stack.addWidget(kaggle_dataset)
        
        repo_layout.addWidget(self.repo_stack)
        cloud_layout.addWidget(repo_frame)
        
        # Add tabs
        self.tabs.addTab(self.local_tab, "Local Export")
        self.tabs.addTab(self.cloud_tab, "Cloud Export")
        
        layout.addWidget(self.tabs)
        
        # Export button
        export_btn = QPushButton(qta.icon("fa5s.file-export"), "Export Dataset")
        export_btn.setObjectName("primary-button")
        export_btn.clicked.connect(self.export_dataset)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(export_btn)
        layout.addLayout(button_layout)
        
        # Set initial states
        self.update_format_options(0)
        self.update_service_options(0)
        
    def load_available_datasets(self):
        datasets_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datasets")
        
        if not os.path.exists(datasets_root):
            return
            
        self.dataset_selector.clear()
        self.dataset_selector.addItem("Select a dataset...", "")
        
        for item in os.listdir(datasets_root):
            item_path = os.path.join(datasets_root, item)
            if os.path.isdir(item_path):
                # Check if it's a valid dataset (has metadata.csv)
                metadata_path = os.path.join(item_path, "metadata.csv")
                if os.path.exists(metadata_path):
                    self.dataset_selector.addItem(item, item_path)
                    
    def load_dataset(self, index):
        if index == 0:  # "Select a dataset..." item
            return
            
        dataset_path = self.dataset_selector.itemData(index)
        dataset_name = self.dataset_selector.itemText(index)
        
        # Set default destination
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.destination_input.setText(os.path.join(desktop_path, f"{dataset_name}_export"))
        
        # Set default Hugging Face dataset name
        self.hf_dataset_name.setText(dataset_name.lower().replace(" ", "_"))
        
        # Set default repository names
        self.hf_repo_name.setText(f"audio-dataset-{dataset_name.lower().replace(' ', '-')}")
        self.github_repo_name.setText(f"audio-dataset-{dataset_name.lower().replace(' ', '-')}")
        self.kaggle_dataset_title.setText(f"Audio Dataset: {dataset_name}")
        
        self.status_bar.showMessage(f"Dataset '{dataset_name}' selected for export", 3000)
        
    def update_format_options(self, index):
        self.format_options_stack.setCurrentIndex(index)
        
    def update_service_options(self, index):
        self.auth_stack.setCurrentIndex(index)
        self.repo_stack.setCurrentIndex(index)
        
    def browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Export Destination")
        if folder:
            self.destination_input.setText(folder)
            
    def export_dataset(self):
        if self.dataset_selector.currentIndex() == 0:
            QMessageBox.warning(self, "Warning", "Please select a dataset to export.")
            return
            
        dataset_path = self.dataset_selector.itemData(self.dataset_selector.currentIndex())
        dataset_name = self.dataset_selector.itemText(self.dataset_selector.currentIndex())
        
        if self.tabs.currentIndex() == 0:  # Local export
            self.export_local(dataset_path, dataset_name)
        else:  # Cloud export
            self.export_cloud(dataset_path, dataset_name)
            
    def export_local(self, dataset_path, dataset_name):
        destination = self.destination_input.text()
        if not destination:
            QMessageBox.warning(self, "Warning", "Please select an export destination.")
            return
            
        # Create destination directory if it doesn't exist
        os.makedirs(destination, exist_ok=True)
        
        # Get metadata
        metadata_path = os.path.join(dataset_path, "metadata.csv")
        try:
            df = pd.read_csv(metadata_path)
        except Exception as e:
            QMessageBox.critical(self, "Error",
