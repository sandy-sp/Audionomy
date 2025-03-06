import plotly.express as px
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtWebEngineWidgets import QWebEngineView
from scripts.dataset_manager import DatasetManager
import tempfile
import pandas as pd

class VisualizationWidget(QWidget):
    def __init__(self, dataset_manager: DatasetManager):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.view = QWebEngineView(self)
        btn_refresh = QPushButton("Refresh Visualization")
        btn_refresh.clicked.connect(self.load_visualization)

        layout.addWidget(self.view)
        layout.addWidget(btn_refresh)

        self.load_visualization()

    def load_visualization(self):
        df = pd.read_csv(self.dataset_manager.metadata_csv)
        if df.empty:
            return

        fig = px.bar(
            df, x='song_title', y='duration', color='style_prompt',
            title="Audionomy Dataset Visualization"
        )

        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            fig.write_html(f.name)
            self.view.load(f'file://{f.name}')
