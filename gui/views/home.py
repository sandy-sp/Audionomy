# Updated home.py for UX improvements
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from scripts.dataset_manager import DatasetManager

class HomeView(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        self.dataset_manager = None
        self.status_bar = status_bar
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("<h1>🎧 Audionomy</h1>"))

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

    def create_dataset(self):
        path = QFileDialog.getExistingDirectory(self, "Choose Dataset Location")
        if path:
            self.dataset_manager = DatasetManager(path)
            try:
                self.dataset_manager.init_metadata()
                QMessageBox.information(self, "Success", f"Dataset created successfully at {path}")
                self.status_bar.showMessage(f"Dataset created at {path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create dataset: {e}")

    def open_dataset(self):
        path = QFileDialog.getExistingDirectory(self, "Open Dataset")
        if path:
            self.dataset_manager = DatasetManager(path)
            self.status_bar.showMessage(f"Dataset loaded from {path}", 5000)

    def visualize_dataset(self):
        if self.dataset_manager:
            self.dataset_manager.visualize()
            self.status_bar.showMessage("Visualization opened", 5000)
        else:
            QMessageBox.warning(self, "No Dataset", "Load a dataset first.")

    def export_dataset(self):
        if self.dataset_manager:
            path = QFileDialog.getExistingDirectory(self, "Export Dataset")
            if path:
                self.dataset_manager.export_all(path)
                self.status_bar.showMessage(f"Exported to {path}", 5000)
        else:
            QMessageBox.warning(self, "No Dataset", "Load a dataset first.")
