from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog
)
from components.entry_form import EntryForm
from scripts.dataset_manager import DatasetManager
import pandas as pd
import os 

class DatasetView(QWidget):
    def __init__(self, dataset_manager: DatasetManager, status_bar):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.status_bar = status_bar
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Dataset: {os.path.basename(self.dataset_manager.dataset_path)}"))

        # Table to display metadata
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Add Entry button
        btn_add = QPushButton("➕ Add Entry")
        btn_add.clicked.connect(self.add_entry)
        layout.addWidget(btn_add)

        # Remove Entry button
        btn_remove = QPushButton("❌ Remove Selected Entry")
        btn_remove.clicked.connect(self.remove_entry)
        layout.addWidget(btn_remove)

        # Visualize Dataset button
        btn_visualize = QPushButton("📊 Visualize Dataset")
        btn_visualize.clicked.connect(self.visualize_dataset)
        layout.addWidget(btn_visualize)

        # Export Dataset button
        btn_export = QPushButton("📥 Export Dataset")
        btn_export.clicked.connect(self.export_dataset)
        layout.addWidget(btn_export)

        # Export to Hugging Face button
        btn_hf_export = QPushButton("🚀 Export to Hugging Face")
        btn_hf_export.clicked.connect(self.export_huggingface)
        layout.addWidget(btn_hf_export)

        # Export to Kaggle button
        btn_kaggle_export = QPushButton("☁️ Export to Kaggle")
        btn_kaggle_export.clicked.connect(self.export_kaggle)
        layout.addWidget(btn_kaggle_export)

        self.setLayout(layout)

    def load_data(self):
        df = pd.read_csv(self.dataset_manager.metadata_csv)
        self.table.clear()
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        self.table.setRowCount(len(df))

        for i, row in df.iterrows():
            for j, col in enumerate(df.columns):
                self.table.setItem(i, j, QTableWidgetItem(str(row[col])))

    def add_entry(self):
        self.entry_form = EntryForm(self.dataset_manager, self.status_bar, self.load_data)
        self.entry_form.setWindowTitle("Add New Audio Entry")
        self.entry_form.show()

    def remove_entry(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            df = pd.read_csv(self.dataset_manager.metadata_csv)
            df = df.drop(df.index[row])
            df.to_csv(self.dataset_manager.metadata_csv, index=False)
            self.load_data()
            self.status_bar.showMessage("Entry removed.", 5000)
        else:
            QMessageBox.warning(self, "Warning", "Please select an entry to remove.")

    def visualize_dataset(self):
        from gui.views.visualization import VisualizationWidget
        self.vis_widget = VisualizationWidget(self.dataset_manager)
        self.vis_widget.show()

    def export_dataset(self):
        export_path = QFileDialog.getExistingDirectory(self, "Export Dataset")
        if export_path:
            self.dataset_manager.export_dataset(export_path)
            QMessageBox.information(self, "Export Complete", f"Dataset exported to {export_path}")
    
    def export_huggingface(self):
        repo_name, ok = QInputDialog.getText(self, "Hugging Face Repo", "Enter repository name (username/repo):")
        if ok and repo_name:
            try:
                self.dataset_manager.export_to_huggingface(repo_name)
                QMessageBox.information(self, "Exported", f"Dataset exported to Hugging Face repo: {repo_name}")
                self.status_bar.showMessage(f"Exported to Hugging Face: {repo_name}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def export_kaggle(self):
        dataset_slug, ok1 = QInputDialog.getText(self, "Kaggle Dataset Slug", "Enter dataset slug (username/dataset-name):")
        if not ok1 or not dataset_slug:
            return
        title, ok2 = QInputDialog.getText(self, "Kaggle Dataset Title", "Enter dataset title:")
        if not ok2 or not title:
            return

        try:
            self.dataset_manager.export_to_kaggle(dataset_slug, title)
            QMessageBox.information(self, "Exported", f"Dataset exported to Kaggle: {dataset_slug}")
            self.status_bar.showMessage(f"Exported to Kaggle: {dataset_slug}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))


