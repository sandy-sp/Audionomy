# gui/views/export_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFrame, QGridLayout, QCheckBox, QFileDialog, QMessageBox, QLineEdit,
    QProgressBar, QFormLayout, QTabWidget, QStackedWidget
)
from PySide6.QtCore import Qt, QThread, Signal
import qtawesome as qta
import os
import pandas as pd
import shutil

from scripts.export_handler import ExportHandler


class ExportWorker(QThread):
    """Handles dataset export in a separate thread to prevent UI freezing."""
    progress_updated = Signal(int)
    export_complete = Signal(bool, str)

    def __init__(self, dataset_path, export_options):
        super().__init__()
        self.dataset_path = dataset_path
        self.export_options = export_options

    def run(self):
        handler = ExportHandler(self.dataset_path, self.export_options)
        success, message = handler.execute_export()
        self.export_complete.emit(success, message)


class ExportView(QWidget):
    """UI for exporting datasets in various formats (local & cloud)."""

    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.export_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize UI layout and components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Export Dataset")
        header.setObjectName("page-header")
        layout.addWidget(header)

        # Dataset Selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Dataset:"))
        self.dataset_selector = QComboBox()
        self.dataset_selector.currentIndexChanged.connect(self.load_dataset)
        selector_layout.addWidget(self.dataset_selector)
        layout.addLayout(selector_layout)

        # Tabs for Local & Cloud Exports
        self.tabs = QTabWidget()

        # Local Export Tab
        self.local_tab = self.create_local_export_tab()
        self.tabs.addTab(self.local_tab, "Local Export")

        # Cloud Export Tab
        self.cloud_tab = self.create_cloud_export_tab()
        self.tabs.addTab(self.cloud_tab, "Cloud Export")

        layout.addWidget(self.tabs)

        # Export Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Export Button
        export_btn = QPushButton(qta.icon("fa5s.file-export"), "Start Export")
        export_btn.setObjectName("primary-button")
        export_btn.clicked.connect(self.start_export)
        layout.addWidget(export_btn)

        # Load Available Datasets
        self.load_available_datasets()

    def create_local_export_tab(self):
        """Creates the UI for local dataset exports."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Export Format Selection
        format_layout = QFormLayout()
        self.format_selector = QComboBox()
        self.format_selector.addItems(["CSV", "JSON", "ZIP Archive"])
        format_layout.addRow("Export Format:", self.format_selector)

        # Destination Folder Selection
        self.destination_input = QLineEdit()
        browse_btn = QPushButton(qta.icon("fa5s.folder-open"), "")
        browse_btn.clicked.connect(self.browse_destination)
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(self.destination_input)
        dest_layout.addWidget(browse_btn)
        format_layout.addRow("Destination:", dest_layout)

        layout.addLayout(format_layout)
        return tab

    def create_cloud_export_tab(self):
        """Creates the UI for cloud exports (Hugging Face, Kaggle, GitHub)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Cloud Service Selector
        self.service_selector = QComboBox()
        self.service_selector.addItems(["Hugging Face", "GitHub", "Kaggle"])
        self.service_selector.currentIndexChanged.connect(self.update_cloud_settings)
        layout.addWidget(QLabel("Select Cloud Service:"))
        layout.addWidget(self.service_selector)

        # Cloud Export Settings
        self.cloud_settings_stack = QStackedWidget()

        # Hugging Face Settings
        hf_widget = QWidget()
        hf_layout = QFormLayout(hf_widget)
        self.hf_repo_name = QLineEdit()
        hf_layout.addRow("Hugging Face Repo:", self.hf_repo_name)
        self.cloud_settings_stack.addWidget(hf_widget)

        # GitHub Settings
        github_widget = QWidget()
        github_layout = QFormLayout(github_widget)
        self.github_repo_name = QLineEdit()
        github_layout.addRow("GitHub Repo:", self.github_repo_name)
        self.cloud_settings_stack.addWidget(github_widget)

        # Kaggle Settings
        kaggle_widget = QWidget()
        kaggle_layout = QFormLayout(kaggle_widget)
        self.kaggle_dataset_title = QLineEdit()
        kaggle_layout.addRow("Kaggle Dataset Title:", self.kaggle_dataset_title)
        self.cloud_settings_stack.addWidget(kaggle_widget)

        layout.addWidget(self.cloud_settings_stack)
        return tab

    def load_available_datasets(self):
        """Populates the dataset selector with available datasets."""
        datasets_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")
        if not os.path.exists(datasets_root):
            return

        self.dataset_selector.clear()
        self.dataset_selector.addItem("Select a dataset...", "")

        for item in os.listdir(datasets_root):
            item_path = os.path.join(datasets_root, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "metadata.csv")):
                self.dataset_selector.addItem(item, item_path)

    def load_dataset(self, index):
        """Loads the selected dataset."""
        if index == 0:
            return

        dataset_path = self.dataset_selector.itemData(index)
        default_destination = os.path.join(os.path.expanduser("~"), "Desktop", f"{os.path.basename(dataset_path)}_export")
        self.destination_input.setText(default_destination)

    def update_cloud_settings(self, index):
        """Switches cloud service settings based on selection."""
        self.cloud_settings_stack.setCurrentIndex(index)

    def browse_destination(self):
        """Opens file dialog to select export destination."""
        folder = QFileDialog.getExistingDirectory(self, "Select Export Destination")
        if folder:
            self.destination_input.setText(folder)

    def start_export(self):
        """Initiates the dataset export process."""
        if self.dataset_selector.currentIndex() == 0:
            QMessageBox.warning(self, "Warning", "Please select a dataset to export.")
            return

        dataset_path = self.dataset_selector.itemData(self.dataset_selector.currentIndex())
        export_options = {
            "format": self.format_selector.currentText(),
            "destination": self.destination_input.text(),
            "service": self.service_selector.currentText(),
            "repo_name": self.hf_repo_name.text() if self.service_selector.currentText() == "Hugging Face" else None,
        }

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.export_worker = ExportWorker(dataset_path, export_options)
        self.export_worker.progress_updated.connect(self.progress_bar.setValue)
        self.export_worker.export_complete.connect(self.handle_export_completion)
        self.export_worker.start()

    def handle_export_completion(self, success, message):
        """Handles export completion and updates UI."""
        self.progress_bar.setVisible(False)
        if success:
            QMessageBox.information(self, "Export Complete", message)
        else:
            QMessageBox.critical(self, "Export Failed", message)
