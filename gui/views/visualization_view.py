# gui/views/visualization_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTabWidget, QFrame, QSplitter, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt
import qtawesome as qta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np
import os

class VisualizationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Dataset Visualization")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Dataset selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Dataset:"))
        self.dataset_selector = QComboBox()
        self.dataset_selector.currentIndexChanged.connect(self.load_dataset)
        selector_layout.addWidget(self.dataset_selector)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Visualization tabs
        self.tabs = QTabWidget()
        
        # Overview tab
        self.overview_tab = QWidget()
        overview_layout = QVBoxLayout(self.overview_tab)
        
        # Stats grid
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
        
        overview_layout.addWidget(stats_frame)
        
        # Charts
        charts_layout = QHBoxLayout()
        
        # Duration distribution
        duration_frame = QFrame()
        duration_frame.setObjectName("section-frame")
        duration_layout = QVBoxLayout(duration_frame)
        duration_layout.addWidget(QLabel("Duration Distribution"))
        
        self.duration_figure, self.duration_ax = plt.subplots(figsize=(5, 4))
        self.duration_canvas = FigureCanvas(self.duration_figure)
        duration_layout.addWidget(self.duration_canvas)
        
        charts_layout.addWidget(duration_frame)
        
        # Format distribution
        format_frame = QFrame()
        format_frame.setObjectName("section-frame")
        format_layout = QVBoxLayout(format_frame)
        format_layout.addWidget(QLabel("Format Distribution"))
        
        self.format_figure, self.format_ax = plt.subplots(figsize=(5, 4))
        self.format_canvas = FigureCanvas(self.format_figure)
        format_layout.addWidget(self.format_canvas)
        
        charts_layout.addWidget(format_frame)
        overview_layout.addLayout(charts_layout)
        
        # Custom charts tab
        self.custom_tab = QWidget()
        custom_layout = QVBoxLayout(self.custom_tab)
        
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
        
        custom_layout.addLayout(controls_layout)
        
        # Custom chart area
        self.custom_figure, self.custom_ax = plt.subplots(figsize=(10, 6))
        self.custom_canvas = FigureCanvas(self.custom_figure)
        custom_layout.addWidget(self.custom_canvas)
        
        # Add tabs
        self.tabs.addTab(self.overview_tab, "Overview")
        self.tabs.addTab(self.custom_tab, "Custom Charts")
        
        layout.addWidget(self.tabs)
        
        # Load available datasets
        self.load_available_datasets()
        
    def load_available_datasets(self):
        datasets_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datasets")
        
        if not os.path.exists(datasets_root):
            return
            
        self.dataset_selector.clear()
        self.dataset_selector.addItem("Select a dataset...", "")
        
        for item in os.listdir(datasets_root):
            item_path = os.path.join(datasets_root, item)
            if os.path.isdir(item_path):
                # Check if it's a valid dataset (has metadata.csv)
                metadata_path = os.path.join(item_path, "metadata.csv")
                if os.path.exists(metadata_path):
                    self.dataset_selector.addItem(item, item_path)
                    
    def load_dataset(self, index):
        if index == 0:  # "Select a dataset..." item
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
        # Update stats
        total_files = len(df)
        self.total_files_label.setText(f"Total Files: {total_files}")
        
        if 'duration' in df.columns:
            total_duration = df['duration'].sum()
            hours, remainder = divmod(total_duration, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.total_duration_label.setText(f"Total Duration: {int(hours)}:{int(minutes):02d}:{int(seconds):02d}")
            
            avg_duration = df['duration'].mean()
            minutes, seconds = divmod(avg_duration, 60)
            self.avg_duration_label.setText(f"Average Duration: {int(minutes)}:{int(seconds):02d}")
        
        if 'file_format' in df.columns:
            formats = df['file_format'].unique()
            self.formats_label.setText(f"File Formats: {', '.join(formats)}")
            
        # Duration distribution chart
        self.duration_ax.clear()
        if 'duration' in df.columns:
            df['duration'].hist(ax=self.duration_ax, bins=20, color='#3498db')
            self.duration_ax.set_xlabel('Duration (seconds)')
            self.duration_ax.set_ylabel('Count')
            self.duration_ax.set_title('Audio Duration Distribution')
            self.duration_canvas.draw()
            
        # Format distribution chart
        self.format_ax.clear()
        if 'file_format' in df.columns:
            format_counts = df['file_format'].value_counts()
            format_counts.plot.pie(ax=self.format_ax, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired(range(len(format_counts))))
            self.format_ax.set_ylabel('')
            self.format_ax.set_title('File Format Distribution')
            self.format_canvas.draw()
            
    def update_custom_chart_options(self, df):
        # Update axis selectors with available columns
        self.x_axis_selector.clear()
        self.y_axis_selector.clear()
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        self.x_axis_selector.addItems(df.columns)
        self.y_axis_selector.addItems(numeric_columns)
        
    def plot_custom_chart(self):
        if self.dataset_selector.currentIndex() == 0:
            return
            
        dataset_path = self.dataset_selector.itemData(self.dataset_selector.currentIndex())
        metadata_path = os.path.join(dataset_path, "metadata.csv")
        
        try:
            df = pd.read_csv(metadata_path)
            
            x_col = self.x_axis_selector.currentText()
            y_col = self.y_axis_selector.currentText()
            chart_type = self.chart_type_selector.currentText()
            
            self.custom_ax.clear()
            
            if chart_type == "Bar Chart":
                if x_col in df.columns and y_col in df.columns:
                    df.groupby(x_col)[y_col].mean().plot.bar(ax=self.custom_ax, color='#3498db')
                    
            elif chart_type == "Scatter Plot":
                if x_col in df.columns and y_col in df.columns:
                    df.plot.scatter(x=x_col, y=y_col, ax=self.custom_ax, color='#3498db')
                    
            elif chart_type == "Line Chart":
                if x_col in df.columns and y_col in df.columns:
                    df.sort_values(x_col).plot.line(x=x_col, y=y_col, ax=self.custom_ax, color='#3498db')
                    
            elif chart_type == "Pie Chart":
                if x_col in df.columns:
                    df[x_col].value_counts().plot.pie(ax=self.custom_ax, autopct='%1.1f%%', colors=plt.cm.Paired(range(len(df[x_col].unique()))))
                    
            self.custom_ax.set_xlabel(x_col)
            self.custom_ax.set_ylabel(y_col)
            self.custom_ax.set_title(f"{chart_type}: {x_col} vs {y_col}")
            self.custom_canvas.draw()
            
        except Exception as e:
            print(f"Error plotting chart: {e}")
