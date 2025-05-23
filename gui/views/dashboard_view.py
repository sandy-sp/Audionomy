# gui/views/dashboard_view.py

import os
import time
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QGridLayout, QLineEdit, QComboBox, 
    QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate, Signal
import qtawesome as qta

from gui.components.dialogs import EnhancedCreateDatasetDialog
from scripts.dataset_manager import DatasetManager
from scripts.logger import logger


class DatasetCard(QFrame):
    """UI representation of an individual dataset."""
    clicked = Signal(str)

    def __init__(self, dataset_path, parent=None):
        super().__init__(parent)
        self.dataset_path = dataset_path
        self.setObjectName("dataset-card")
        self.setFixedSize(280, 180)
        self.setCursor(Qt.PointingHandCursor)
        self.setup_ui()

    def setup_ui(self):
        """Creates the dataset card layout."""
        layout = QVBoxLayout(self)

        # Dataset name
        self.name_label = QLabel(os.path.basename(self.dataset_path))
        self.name_label.setObjectName("card-title")
        layout.addWidget(self.name_label)

        # Stats grid
        stats_layout = QGridLayout()
        
        # Count audio files
        audio_dir = os.path.join(self.dataset_path, "audio")
        audio_count = len(os.listdir(audio_dir)) if os.path.exists(audio_dir) else 0

        # Get metadata info
        metadata_path = os.path.join(self.dataset_path, "metadata.csv")
        columns_count = 0
        if os.path.exists(metadata_path):
            try:
                df = pd.read_csv(metadata_path)
                columns_count = len(df.columns)
            except:
                pass

        # Display stats
        stats_layout.addWidget(QLabel(qta.icon("fa5s.file-audio", color="#3498db"), f" {audio_count}"), 0, 0)
        stats_layout.addWidget(QLabel("Audio Files"), 0, 1)
        stats_layout.addWidget(QLabel(qta.icon("fa5s.columns", color="#2ecc71"), f" {columns_count}"), 1, 0)
        stats_layout.addWidget(QLabel("Columns"), 1, 1)

        layout.addLayout(stats_layout)
        layout.addStretch()

        # Clickable Action Buttons
        actions_layout = QHBoxLayout()
        visualize_btn = QPushButton(qta.icon("fa5s.chart-bar"), "")
        visualize_btn.setToolTip("Visualize Dataset")
        visualize_btn.setObjectName("card-button")

        export_btn = QPushButton(qta.icon("fa5s.file-export"), "")
        export_btn.setToolTip("Export Dataset")
        export_btn.setObjectName("card-button")

        actions_layout.addWidget(visualize_btn)
        actions_layout.addWidget(export_btn)
        layout.addLayout(actions_layout)

    def mousePressEvent(self, event):
        """Emits signal when a dataset card is clicked."""
        super().mousePressEvent(event)
        self.clicked.emit(self.dataset_path)


class DashboardWidget(QWidget):
    """Main dashboard displaying all datasets with search, sorting, and filtering options."""
    datasetSelected = Signal(str)

    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.datasets_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datasets")
        self.dataset_cards = []  # List of dataset cards for filtering
        self.setup_ui()

    def setup_ui(self):
        """Initialize UI layout and dataset grid."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        header = QLabel("Your Datasets")
        header.setObjectName("page-header")
        header_layout.addWidget(header)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search datasets...")
        self.search_input.textChanged.connect(self.load_datasets)
        header_layout.addWidget(self.search_input)

        # Create Dataset Button
        create_btn = QPushButton(qta.icon("fa5s.plus"), "New Dataset")
        create_btn.setObjectName("primary-button")
        create_btn.clicked.connect(self.create_dataset)
        header_layout.addWidget(create_btn)

        layout.addLayout(header_layout)

        # Filters Layout
        filters_layout = QHBoxLayout()

        # Sort By Filter
        self.sort_filter = QComboBox()
        self.sort_filter.addItems(["Sort by...", "Creation Date", "Last Modified"])
        self.sort_filter.currentIndexChanged.connect(self.load_datasets)
        filters_layout.addWidget(self.sort_filter)

        # Creation Date Filter
        self.creation_date_filter = QDateEdit()
        self.creation_date_filter.setCalendarPopup(True)
        self.creation_date_filter.setDisplayFormat("yyyy-MM-dd")
        self.creation_date_filter.setDate(QDate.currentDate())
        self.creation_date_filter.dateChanged.connect(self.load_datasets)
        filters_layout.addWidget(QLabel("Filter by Creation Date:"))
        filters_layout.addWidget(self.creation_date_filter)

        # Last Modified Date Filter
        self.modified_date_filter = QDateEdit()
        self.modified_date_filter.setCalendarPopup(True)
        self.modified_date_filter.setDisplayFormat("yyyy-MM-dd")
        self.modified_date_filter.setDate(QDate.currentDate())
        self.modified_date_filter.dateChanged.connect(self.load_datasets)
        filters_layout.addWidget(QLabel("Filter by Last Modified Date:"))
        filters_layout.addWidget(self.modified_date_filter)

        layout.addLayout(filters_layout)

        # Dataset Grid with Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(20)
        self.scroll_area.setWidget(scroll_content)

        layout.addWidget(self.scroll_area)

        # Load datasets
        self.load_datasets()

    def create_dataset(self):
        """Opens the create dataset dialog and refreshes dashboard."""
        logger.info("Opening Create Dataset Dialog")
        dialog = EnhancedCreateDatasetDialog(self)
        if dialog.exec():
            dataset_name, dataset_path, columns = dialog.get_data()
            full_path = os.path.join(dataset_path, dataset_name)
            os.makedirs(full_path, exist_ok=True)

            dataset_manager = DatasetManager(full_path, create_new=True, columns=columns)
            dataset_manager.init_metadata()

            self.status_bar.showMessage(f"Dataset '{dataset_name}' created successfully", 5000)
            logger.info(f"Dataset created: {dataset_name}")
            self.load_datasets()
            self.datasetSelected.emit(full_path)

    def load_datasets(self):
        """Loads datasets with filtering and sorting applied."""
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.dataset_cards.clear()

        if not os.path.exists(self.datasets_root):
            os.makedirs(self.datasets_root)

        datasets = [
            os.path.join(self.datasets_root, item)
            for item in os.listdir(self.datasets_root)
            if os.path.isdir(os.path.join(self.datasets_root, item))
        ]

        for dataset_path in datasets:
            card = DatasetCard(dataset_path)
            card.clicked.connect(self.on_dataset_selected)
            self.grid_layout.addWidget(card)
            self.dataset_cards.append((dataset_path, card))

    def on_dataset_selected(self, dataset_path):
        """Handles dataset selection and emits a signal."""
        self.datasetSelected.emit(dataset_path)
