# gui/views/dataset_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QTabWidget,
    QSplitter, QFrame, QMenu, QToolBar, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction
import qtawesome as qta
import os
import pandas as pd

from gui.components.audio_player import AudioWaveformWidget

class DatasetView(QWidget):
    def __init__(self, dataset_manager, status_bar, parent=None):
        super().__init__(parent)
        self.dataset_manager = dataset_manager
        self.status_bar = status_bar
        self.setup_ui()
        self.load_dataset()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with dataset name and actions
        header_layout = QHBoxLayout()
        self.dataset_name_label = QLabel()
        self.dataset_name_label.setObjectName("page-header")
        header_layout.addWidget(self.dataset_name_label)
        
        # Toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # Add audio files action
        add_audio_action = QAction(qta.icon("fa5s.file-audio"), "Add Audio Files", self)
        add_audio_action.triggered.connect(self.add_audio_files)
        toolbar.addAction(add_audio_action)
        
        # Export action
        export_action = QAction(qta.icon("fa5s.file-export"), "Export Dataset", self)
        export_action.triggered.connect(self.export_dataset)
        toolbar.addAction(export_action)
        
        # Visualize action
        visualize_action = QAction(qta.icon("fa5s.chart-bar"), "Visualize", self)
        visualize_action.triggered.connect(self.visualize_dataset)
        toolbar.addAction(visualize_action)
        
        # Settings action
        settings_action = QAction(qta.icon("fa5s.cog"), "Settings", self)
        settings_action.triggered.connect(self.dataset_settings)
        toolbar.addAction(settings_action)
        
        header_layout.addWidget(toolbar)
        layout.addLayout(header_layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Table view for metadata
        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in metadata...")
        self.search_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Column:"))
        self.column_filter = QComboBox()
        filter_layout.addWidget(self.column_filter)
        
        table_layout.addLayout(filter_layout)
        
        # Metadata table
        self.metadata_table = QTableWidget()
        self.metadata_table.setAlternatingRowColors(True)
        self.metadata_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.metadata_table.setEditTriggers(QTableWidget.DoubleClicked)
        self.metadata_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.metadata_table.cellChanged.connect(self.on_cell_changed)
        self.metadata_table.cellClicked.connect(self.on_cell_clicked)
        table_layout.addWidget(self.metadata_table)
        
        splitter.addWidget(table_frame)
        
        # Audio player
        player_frame = QFrame()
        player_layout = QVBoxLayout(player_frame)
        player_layout.addWidget(QLabel("Audio Preview"))
        
        self.audio_player = AudioWaveformWidget()
        player_layout.addWidget(self.audio_player)
        
        splitter.addWidget(player_frame)
        
        # Set initial sizes
        splitter.setSizes([600, 200])
        
        layout.addWidget(splitter)
        
    def load_dataset(self):
        # Set dataset name
        dataset_name = os.path.basename(self.dataset_manager.dataset_path)
        self.dataset_name_label.setText(dataset_name)
        
        # Load metadata
        metadata = self.dataset_manager.get_metadata()
        if metadata is None:
            QMessageBox.warning(self, "Error", "Failed to load dataset metadata.")
            return
            
        # Setup table
        self.metadata_table.setRowCount(len(metadata))
        self.metadata_table.setColumnCount(len(metadata.columns))
        self.metadata_table.setHorizontalHeaderLabels(metadata.columns)
        
        # Populate column filter
        self.column_filter.clear()
        self.column_filter.addItem("All Columns")
        self.column_filter.addItems(metadata.columns)
        
        # Fill table
        for row in range(len(metadata)):
            for col in range(len(metadata.columns)):
                value = str(metadata.iloc[row, col])
                item = QTableWidgetItem(value)
                self.metadata_table.setItem(row, col, item)
                
        self.status_bar.showMessage(f"Loaded dataset with {len(metadata)} entries", 5000)
        
    def add_audio_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Audio Files", 
            "", 
            "Audio Files (*.mp3 *.wav *.flac *.ogg *.aac)"
        )
        
        if not files:
            return
            
        # Add files to dataset
        added_count = self.dataset_manager.add_audio_files(files)
        
        if added_count > 0:
            self.status_bar.showMessage(f"Added {added_count} audio files to dataset", 5000)
            self.load_dataset()  # Reload to show new files
        else:
            QMessageBox.warning(self, "Warning", "No files were added to the dataset.")
            
    def export_dataset(self):
        # This would open the export dialog
        self.status_bar.showMessage("Export functionality not implemented yet", 5000)
        
    def visualize_dataset(self):
        # This would switch to visualization view with this dataset
        self.status_bar.showMessage("Visualization functionality not implemented yet", 5000)
        
    def dataset_settings(self):
        # This would open dataset settings dialog
        self.status_bar.showMessage("Settings functionality not implemented yet", 5000)
        
    def on_cell_changed(self, row, column):
        # Get the changed value
        new_value = self.metadata_table.item(row, column).text()
        column_name = self.metadata_table.horizontalHeaderItem(column).text()
        
        # Update the metadata
        self.dataset_manager.update_metadata_value(row, column_name, new_value)
        self.status_bar.showMessage(f"Updated {column_name} for row {row+1}", 3000)
        
    def on_cell_clicked(self, row, column):
        # Check if this is a filename column
        column_name = self.metadata_table.horizontalHeaderItem(column).text()
        if column_name == "filename":
            filename = self.metadata_table.item(row, column).text()
            audio_path = os.path.join(self.dataset_manager.dataset_path, "audio", filename)
            
            if os.path.exists(audio_path):
                self.audio_player.load_audio(audio_path)
                self.status_bar.showMessage(f"Playing: {filename}", 3000)
            else:
                self.status_bar.showMessage(f"Audio file not found: {filename}", 3000)
                
    def filter_table(self):
        search_text = self.search_input.text().lower()
        column_idx = self.column_filter.currentIndex() - 1  # -1 because "All Columns" is first
        
        for row in range(self.metadata_table.rowCount()):
            match_found = False
            
            if column_idx >= 0:  # Specific column
                cell_text = self.metadata_table.item(row, column_idx).text().lower()
                match_found = search_text in cell_text
            else:  # All columns
                for col in range(self.metadata_table.columnCount()):
                    cell_text = self.metadata_table.item(row, col).text().lower()
                    if search_text in cell_text:
                        match_found = True
                        break
                        
            self.metadata_table.setRowHidden(row, not match_found)
