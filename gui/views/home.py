from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from scripts.dataset_manager import DatasetManager
from components.dialogs import CreateDatasetDialog

class HomeView(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar
        self.dataset_manager = None
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

        btn_add_entry = QPushButton("➕ Add Audio Entry")
        btn_add_entry.clicked.connect(self.add_audio_entry)
        layout.addWidget(btn_add_entry)

        btn_visualize = QPushButton("📊 Visualize Dataset")
        btn_visualize.clicked.connect(self.visualize_dataset)
        layout.addWidget(btn_visualize)

        btn_export = QPushButton("📥 Export Dataset")
        btn_export.clicked.connect(self.export_dataset)
        layout.addWidget(btn_export)

    def create_dataset(self):
        dialog = CreateDatasetDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            dataset_path = os.path.join(data['save_path'], data['dataset_name'])
            os.makedirs(dataset_path, exist_ok=True)
            self.dataset_manager = DatasetManager(dataset_path)
            self.dataset_manager.init_metadata()
            QMessageBox.information(self, "Success", f"Dataset created at {dataset_path}")
            self.status_bar.showMessage(f"Dataset created at {dataset_path}", 5000)

    def open_dataset(self):
        path = QFileDialog.getExistingDirectory(self, "Open Dataset")
        if path:
            self.dataset_manager = DatasetManager(path)
            QMessageBox.information(self, "Loaded", f"Dataset loaded from {path}")
            self.status_bar.showMessage(f"Dataset loaded from {path}", 5000)

    def add_audio_entry(self):
        if not self.dataset_manager:
            QMessageBox.warning(self, "No Dataset", "Please load/create a dataset first.")
            return
        QMessageBox.information(self, "Coming Soon", "Audio entry form integration will be next!")

    def visualize_dataset(self):
        if self.dataset_manager:
            self.dataset_manager.visualize()
            self.status_bar.showMessage("Visualization opened", 5000)
        else:
            QMessageBox.warning(self, "No Dataset", "Load a dataset first.")

    def export_dataset(self):
        if self.dataset_manager:
            export_path = QFileDialog.getExistingDirectory(self, "Export Dataset")
            if export_path:
                self.dataset_manager.export_all(export_path)
                QMessageBox.information(self, "Exported", f"Dataset exported to {export_path}")
                self.status_bar.showMessage(f"Dataset exported to {export_path}", 5000)
        else:
            QMessageBox.warning(self, "No Dataset", "Load a dataset first.")
