from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt  # ✅ Fix: added missing import
from components.dialogs import CreateDatasetDialog
from scripts.dataset_manager import DatasetManager
import os
from gui.views.visualization import VisualizationWidget
from PySide6.QtWidgets import QFileDialog
from gui.views.dataset_view import DatasetView

class HomeView(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar
        self.dataset_manager = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("<h2>🎧 Audionomy Dataset Manager</h2>"))

        btn_create = QPushButton("📁 Create New Dataset")
        btn_create.clicked.connect(self.create_dataset)
        layout.addWidget(btn_create)

        btn_open = QPushButton("📂 Open Existing Dataset")
        btn_open.clicked.connect(self.open_dataset)
        layout.addWidget(btn_open)

    def create_dataset(self):
        dialog = CreateDatasetDialog(self)
        if dialog.exec():
            dataset_name, dataset_path, columns = dialog.get_data()
            full_path = os.path.join(dataset_path, dataset_name)
            os.makedirs(full_path, exist_ok=True)

            self.dataset_manager = DatasetManager(full_path, create_new=True, columns=columns)
            self.dataset_manager.init_metadata()

            QMessageBox.information(self, "Success", f"Dataset '{dataset_name}' created successfully!")
            self.status_bar.showMessage(f"Dataset '{dataset_name}' created.", 5000)
            self.switch_to_dataset_view()  # transition clearly after creation


    def open_dataset(self):
        path = QFileDialog.getExistingDirectory(self, "Open Dataset")
        if path:
            template_files = [f for f in os.listdir(path) if f.endswith('.template')]
            if not template_files:
                QMessageBox.critical(self, "Invalid Dataset", "No valid .template file found in this folder!")
                return

            self.dataset_manager = DatasetManager(path)
            self.status_bar.showMessage(f"Dataset '{os.path.basename(path)}' loaded", 5000)
            self.switch_to_dataset_view()  # transition to dedicated view

    def visualize_dataset(self):
        if not self.dataset_manager:
            QMessageBox.warning(self, "Error", "Load or create a dataset first.")
            return

        self.vis_widget = VisualizationWidget(self.dataset_manager)
        self.vis_widget.setWindowTitle("Dataset Visualization")
        self.vis_widget.resize(800, 600)
        self.vis_widget.show()

    def export_dataset(self):
        if not self.dataset_manager:
            QMessageBox.warning(self, "Error", "Load or create a dataset first.")
            return

        export_path = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if export_path:
            self.dataset_manager.export_dataset(export_path)
            QMessageBox.information(self, "Export Complete", f"Dataset exported to {export_path}")
    
    def switch_to_dataset_view(self):
        self.dataset_view = DatasetView(self.dataset_manager, self.status_bar)
        self.window().setCentralWidget(self.dataset_view)