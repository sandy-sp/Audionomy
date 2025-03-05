# gui/views/home.py
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

        layout.addWidget(QLabel("Welcome to Audionomy!"))

        btn_create_dataset = QPushButton("📁 Create New Dataset")
        btn_create_dataset.clicked.connect(self.create_dataset)
        layout.addWidget(btn_create_dataset)

        btn_open_dataset = QPushButton("📂 Open Existing Dataset")
        btn_open_dataset.clicked.connect(self.open_dataset)
        layout.addWidget(btn_open_dataset)

        btn_visualize = QPushButton("📊 Visualize Dataset")
        btn_visualize.clicked.connect(self.visualize_dataset)  # Fix is here
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
            dataset_path = os.path.join(data['save_path'], data['dataset_name'])
            os.makedirs(dataset_path, exist_ok=True)
            self.dataset_manager = DatasetManager(dataset_path)
            self.dataset_manager.init_metadata()
            QMessageBox.information(self, "Success", f"Dataset '{data['dataset_name']}' created at {dataset_path}")

    def open_dataset(self):
        dataset_path = QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
        if dataset_path:
            self.dataset_manager = DatasetManager(dataset_path)
            self.refresh_table()
            QMessageBox.information(self, "Dataset Loaded", f"Dataset loaded from {dataset_path}")

    def refresh_table(self):
        if self.dataset_manager:
            df = self.dataset_manager.load_metadata()
            if df.empty:
                QMessageBox.information(self, "Empty Dataset", "This dataset currently has no entries.")
                return

            table = QTableWidget(len(df), len(df.columns), self)
            table.setHorizontalHeaderLabels(df.columns.tolist())

            for i, row in df.iterrows():
                for j, val in enumerate(row):
                    table.setItem(i, j, QTableWidgetItem(str(val)))

            layout = self.layout()
            layout.addWidget(table)

    def open_dataset(self):
        dataset_path = QFileDialog.getExistingDirectory(self, "Select Dataset")
        if dataset_path:
            self.dataset_manager = DatasetManager(dataset_path)
            self.refresh_table()

    def visualize_dataset(self):
        if self.dataset_manager:
            df = self.dataset_manager.load_metadata()
            if df.empty:
                QMessageBox.warning(self, "No Data", "No data available for visualization.")
                return
            fig = px.bar(df, x='song_title', y='duration', title='Audio Durations')
            fig.show()

    def export_dataset(self):
        if self.dataset_manager:
            export_path = QFileDialog.getExistingDirectory(self, "Export Dataset To")
            if export_path:
                self.dataset_manager.export_all(export_path)
                QMessageBox.information(self, "Exported", f"Dataset exported to {export_path}")
