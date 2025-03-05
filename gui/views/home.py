# Updated home.py with enhanced error handling
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem
)
from components.dialogs import CreateDatasetDialog
from scripts.dataset_manager import DatasetManager
import os
import plotly.express as px
import pandas as pd

class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.dataset_manager = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Welcome to Audionomy!", self))

        btn_create = QPushButton("📁 Create New Dataset")
        btn_create.clicked.connect(self.create_dataset)
        layout.addWidget(btn_create)

        btn_open = QPushButton("📂 Open Existing Dataset")
        btn_open.clicked.connect(self.open_dataset)
        layout.addWidget(btn_open)

        btn_visualize = QPushButton("📊 Visualize Dataset")
        btn_visualize.clicked.connect(self.visualize_dataset)
        layout.addWidget(btn_visualize)

        btn_export = QPushButton("📥 Export Dataset")
        btn_export.clicked.connect(self.export_dataset)
        layout.addWidget(btn_export)

        self.table = QTableWidget()
        layout.addWidget(self.table)

    def create_dataset(self):
        dialog = CreateDatasetDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                dataset_path = os.path.join(data['save_path'], data['dataset_name'])
                os.makedirs(dataset_path, exist_ok=True)
                self.dataset_manager = DatasetManager(dataset_path)
                self.dataset_manager.init_metadata()
                QMessageBox.information(self, "Success", f"Dataset '{data['dataset_name']}' created successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Creation Error", str(e))

    def open_dataset(self):
        try:
            dataset_path = QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
            if dataset_path:
                self.dataset_manager = DatasetManager(dataset_path)
                self.refresh_table()
                QMessageBox.information(self, "Loaded", f"Dataset loaded from {dataset_path}")
        except Exception as e:
            QMessageBox.critical(self, "Loading Error", str(e))

    def refresh_table(self):
        if not self.dataset_manager:
            QMessageBox.warning(self, "No Dataset", "Please load or create a dataset first.")
            return

        df = self.dataset_manager.load_metadata()
        self.table.clear()

        if df.empty:
            QMessageBox.information(self, "Empty Dataset", "No entries in the dataset.")
            return

        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels(df.columns)

        for i, row in df.iterrows():
            for j, (col, val) in enumerate(row.items()):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def visualize_dataset(self):
        if not self.dataset_manager:
            QMessageBox.warning(self, "No Dataset", "Please load or create a dataset first.")
            return

        df = self.dataset_manager.load_metadata()
        if df.empty:
            QMessageBox.warning(self, "Empty Dataset", "Dataset contains no entries to visualize.")
            return

        fig = px.bar(df, x='song_title', y='duration', title="Audio Duration Visualization")
        fig.show()

    def export_dataset(self):
        if not self.dataset_manager:
            QMessageBox.warning(self, "No Dataset", "Please load or create a dataset first.")
            return

        export_path = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if export_path:
            try:
                self.dataset_manager.export_all(export_path)
                QMessageBox.information(self, "Export Complete", f"Dataset exported to {export_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
