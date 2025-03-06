# gui/views/visualization_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTabWidget, QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt
import qtawesome as qta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np
import os


class VisualizationWidget(QWidget):
    """Visualization module for dataset insights, statistics, and charts."""

    def __init__(self, dataset_manager, parent=None):
        super().__init__(parent)
        self.dataset_manager = dataset_manager
        self.dataset_path = dataset_manager.dataset_path
        self.setup_ui()

    def setup_ui(self):
        """Set up the layout and components for dataset visualization."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Dataset Visualization")
        header.setObjectName("page-header")
        layout.addWidget(header)

        # Dataset Selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Dataset:"))
        self.dataset_selector = QComboBox()
        self.dataset_selector.currentIndexChanged.connect(self.load_dataset)
        selector_layout.addWidget(self.dataset_selector)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        # Visualization Tabs
        self.tabs = QTabWidget()

        # Overview Tab (Dataset Statistics)
        self.overview_tab = QWidget()
        overview_layout = QVBoxLayout(self.overview_tab)

        stats_frame = self.create_stats_section()
        overview_layout.addWidget(stats_frame)

        # Dataset Charts
        charts_layout = QHBoxLayout()
        self.duration_chart = self.create_chart("Duration Distribution")
        self.format_chart = self.create_chart("Format Distribution")
        charts_layout.addWidget(self.duration_chart)
        charts_layout.addWidget(self.format_chart)

        overview_layout.addLayout(charts_layout)
        self.tabs.addTab(self.overview_tab, "Overview")

        # Custom Charts Tab
        self.custom_tab = QWidget()
        custom_layout = QVBoxLayout(self.custom_tab)

        # Chart Controls
        controls_layout = self.create_chart_controls()
        custom_layout.addLayout(controls_layout)

        # Custom Chart Canvas
        self.custom_figure, self.custom_ax = plt.subplots(figsize=(10, 6))
        self.custom_canvas = FigureCanvas(self.custom_figure)
        custom_layout.addWidget(self.custom_canvas)

        self.tabs.addTab(self.custom_tab, "Custom Charts")

        layout.addWidget(self.tabs)

        # Load Available Datasets
        self.load_available_datasets()

    def create_stats_section(self):
        """Creates a frame containing dataset statistics."""
        stats_frame = QFrame()
        stats_frame.setObjectName("section-frame")
        stats_layout = QGridLayout(stats_frame)

        self.total_files_label = QLabel("Total Files: 0")
        stats_layout.addWidget(self.total_files_label, 0, 0)

        self.total_duration_label = QLabel("Total Duration: 0:00:00")
        stats_layout.addWidget(self.total_duration_label, 0, 1)

        self.avg_duration_label = QLabel("Average Duration: 0:00")
        stats_layout.addWidget(self.avg_duration_label, 1, 0)

        self.formats_label = QLabel("File Formats: -")
        stats_layout.addWidget(self.formats_label, 1, 1)

        return stats_frame

    def create_chart(self, title):
        """Creates a chart placeholder with title."""
        frame = QFrame()
        frame.setObjectName("section-frame")
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel(title))

        figure, ax = plt.subplots(figsize=(5, 4))
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)

        return frame

    def create_chart_controls(self):
        """Creates controls for custom chart selection."""
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("X Axis:"))
        self.x_axis_selector = QComboBox()
        controls_layout.addWidget(self.x_axis_selector)

        controls_layout.addWidget(QLabel("Y Axis:"))
        self.y_axis_selector = QComboBox()
        controls_layout.addWidget(self.y_axis_selector)

        controls_layout.addWidget(QLabel("Chart Type:"))
        self.chart_type_selector = QComboBox()
        self.chart_type_selector.addItems(["Bar Chart", "Scatter Plot", "Line Chart", "Pie Chart"])
        controls_layout.addWidget(self.chart_type_selector)

        plot_btn = QPushButton(qta.icon("fa5s.chart-line"), "Plot")
        plot_btn.clicked.connect(self.plot_custom_chart)
        controls_layout.addWidget(plot_btn)

        return controls_layout

    def load_available_datasets(self):
        """Loads datasets into the selector."""
        datasets_root = os.path.dirname(self.dataset_path)
        if not os.path.exists(datasets_root):
            return

        self.dataset_selector.clear()
        self.dataset_selector.addItem("Select a dataset...", "")

        for item in os.listdir(datasets_root):
            item_path = os.path.join(datasets_root, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "metadata.csv")):
                self.dataset_selector.addItem(item, item_path)

    def load_dataset(self, index):
        """Loads dataset metadata and updates statistics & charts."""
        if index == 0:  # Ignore first placeholder option
            return

        dataset_path = self.dataset_selector.itemData(index)
        metadata_path = os.path.join(dataset_path, "metadata.csv")

        try:
            df = pd.read_csv(metadata_path)
            self.update_overview(df, dataset_path)
            self.update_custom_chart_options(df)
        except Exception as e:
            print(f"Error loading dataset: {e}")

    def update_overview(self, df, dataset_path):
        """Updates dataset statistics and default charts."""
        self.total_files_label.setText(f"Total Files: {len(df)}")

        if 'duration' in df.columns:
            total_duration = df['duration'].sum()
            avg_duration = df['duration'].mean()
            self.total_duration_label.setText(f"Total Duration: {int(total_duration // 60)} min")
            self.avg_duration_label.setText(f"Average Duration: {int(avg_duration)} sec")

        if 'file_format' in df.columns:
            formats = df['file_format'].unique()
            self.formats_label.setText(f"File Formats: {', '.join(formats)}")

    def update_custom_chart_options(self, df):
        """Updates available X and Y axis options for custom charts."""
        self.x_axis_selector.clear()
        self.y_axis_selector.clear()

        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        self.x_axis_selector.addItems(df.columns)
        self.y_axis_selector.addItems(numeric_columns)

    def plot_custom_chart(self):
        """Generates a chart based on user-selected options."""
        dataset_path = self.dataset_selector.itemData(self.dataset_selector.currentIndex())
        metadata_path = os.path.join(dataset_path, "metadata.csv")

        try:
            df = pd.read_csv(metadata_path)
            x_col = self.x_axis_selector.currentText()
            y_col = self.y_axis_selector.currentText()
            chart_type = self.chart_type_selector.currentText()

            self.custom_ax.clear()
            if chart_type == "Bar Chart":
                df.groupby(x_col)[y_col].mean().plot.bar(ax=self.custom_ax, color='#3498db')
            elif chart_type == "Scatter Plot":
                df.plot.scatter(x=x_col, y=y_col, ax=self.custom_ax, color='#3498db')
            elif chart_type == "Line Chart":
                df.sort_values(x_col).plot.line(x=x_col, y=y_col, ax=self.custom_ax, color='#3498db')
            elif chart_type == "Pie Chart":
                df[x_col].value_counts().plot.pie(ax=self.custom_ax, autopct='%1.1f%%')

            self.custom_canvas.draw()
        except Exception as e:
            print(f"Error plotting chart: {e}")
