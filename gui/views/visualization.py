import os
import pandas as pd
import plotly.express as px
import tempfile
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from scripts.dataset_manager import DatasetManager

class VisualizationWidget(QWidget):
    def __init__(self, dataset_manager: DatasetManager):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.setWindowTitle("Dataset Visualization")
        self.resize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.web_view = QWebEngineView()
        refresh_btn = QPushButton("🔄 Refresh Visualization")
        refresh_btn.clicked.connect(self.load_visualization)

        layout.addWidget(self.web_view)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)
        self.load_visualization()

    def load_visualization(self):
        df = pd.read_csv(self.dataset_manager.metadata_csv)
        if df.empty:
            QMessageBox.warning(self, "No Data", "The dataset is currently empty.")
            return

        fig = px.bar(
            df, x='song_title', y='duration', color='style_prompt',
            title="Audionomy Dataset: Audio Duration by Song Title"
        )
        temp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        fig.write_html(temp_html.name)
        self.web_view.load(f"file://{temp_html.name}")
