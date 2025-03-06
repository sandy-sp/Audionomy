# gui/views/dashboard_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QGridLayout, QInputDialog
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
import os
import json
import pandas as pd

from gui.components.dialogs import EnhancedCreateDatasetDialog
from scripts.dataset_manager import DatasetManager

class DatasetCard(QFrame):
    clicked = Signal(str)
    
    def __init__(self, dataset_path, parent=None):
        super().__init__(parent)
        self.dataset_path = dataset_path
        self.setObjectName("dataset-card")
        self.setFixedSize(280, 180)
        self.setCursor(Qt.PointingHandCursor)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Dataset name
        self.name_label = QLabel(os.path.basename(self.dataset_path))
        self.name_label.setObjectName("card-title")
        layout.addWidget(self.name_label)
        
        # Stats
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
        
        # Action buttons
        actions_layout = QHBoxLayout()
        edit_btn = QPushButton(qta.icon("fa5s.edit"), "")
        edit_btn.setToolTip("Edit Dataset")
        edit_btn.setObjectName("card-button")
        
        visualize_btn = QPushButton(qta.icon("fa5s.chart-bar"), "")
        visualize_btn.setToolTip("Visualize Dataset")
        visualize_btn.setObjectName("card-button")
        
        export_btn = QPushButton(qta.icon("fa5s.file-export"), "")
        export_btn.setToolTip("Export Dataset")
        export_btn.setObjectName("card-button")
        
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(visualize_btn)
        actions_layout.addWidget(export_btn)
        layout.addLayout(actions_layout)
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self.dataset_path)

class DashboardWidget(QWidget):
    datasetSelected = Signal(str)
    
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.datasets_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datasets")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("Your Datasets")
        header.setObjectName("page-header")
        header_layout.addWidget(header)
        
        create_btn = QPushButton(qta.icon("fa5s.plus"), "New Dataset")
        create_btn.setObjectName("primary-button")
        create_btn.clicked.connect(self.create_dataset)
        header_layout.addStretch()
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Datasets grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(20)
        scroll_area.setWidget(scroll_content)
        
        layout.addWidget(scroll_area)
        
        # Load datasets
        self.load_datasets()
        
    def load_datasets(self):
        # Clear existing items
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Find all datasets
        if not os.path.exists(self.datasets_root):
            os.makedirs(self.datasets_root)
            
        datasets = []
        for item in os.listdir(self.datasets_root):
            item_path = os.path.join(self.datasets_root, item)
            if os.path.isdir(item_path):
                # Check if it's a valid dataset (has template file)
                for file in os.listdir(item_path):
                    if file.endswith('.template'):
                        datasets.append(item_path)
                        break
        
        # Add dataset cards to grid
        row, col = 0, 0
        max_cols = 3
        
        for dataset_path in datasets:
            card = DatasetCard(dataset_path)
            card.clicked.connect(self.on_dataset_selected)
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
        # Add empty state if no datasets
        if not datasets:
            empty_label = QLabel("No datasets found. Create your first dataset to get started!")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setObjectName("empty-state")
            self.grid_layout.addWidget(empty_label, 0, 0, 1, max_cols)
            
    def on_dataset_selected(self, dataset_path):
        self.datasetSelected.emit(dataset_path)
        
    def create_dataset(self):
        dialog = EnhancedCreateDatasetDialog(self)
        if dialog.exec():
            dataset_name, dataset_path, columns = dialog.get_data()
            full_path = os.path.join(dataset_path, dataset_name)
            os.makedirs(full_path, exist_ok=True)

            dataset_manager = DatasetManager(full_path, create_new=True, columns=columns)
            dataset_manager.init_metadata()

            self.status_bar.showMessage(f"Dataset '{dataset_name}' created successfully", 5000)
            self.load_datasets()
            self.datasetSelected.emit(full_path)
