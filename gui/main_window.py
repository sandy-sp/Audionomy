# gui/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame, QStatusBar
)
from PySide6.QtCore import Qt
import qtawesome as qta

from gui.views.dashboard_view import DashboardWidget
from gui.views.dataset_view import DatasetView
from gui.views.visualization_view import VisualizationWidget
from gui.views.export_view import ExportView
from gui.views.settings_view import SettingsView

class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audionomy")
        self.setWindowIcon(qta.icon('fa5s.headphones-alt'))
        self.resize(1200, 800)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Welcome to Audionomy")
        
        # Main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # App logo
        logo_layout = QHBoxLayout()
        logo_icon = QLabel()
        logo_icon.setPixmap(qta.icon("fa5s.headphones-alt", color="#3498db").pixmap(32, 32))
        logo_text = QLabel("Audionomy")
        logo_text.setObjectName("logo-text")
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        sidebar_layout.addLayout(logo_layout)
        sidebar_layout.addSpacing(20)
        
        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("dashboard", "Dashboard", "fa5s.home"),
            ("datasets", "Datasets", "fa5s.database"),
            ("visualize", "Visualize", "fa5s.chart-bar"),
            ("export", "Export", "fa5s.file-export"),
            ("settings", "Settings", "fa5s.cog")
        ]
        
        for item_id, label, icon in nav_items:
            btn = QPushButton(qta.icon(icon, color="#ffffff"), f" {label}")
            btn.setObjectName(f"nav-{item_id}")
            btn.setCheckable(True)
            btn.setProperty("navButton", True)
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        sidebar_layout.addStretch()
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("content-stack")
        
        # Add pages to stack
        self.dashboard_page = DashboardWidget(self.status_bar)
        self.dashboard_page.datasetSelected.connect(self.open_dataset)
        
        self.datasets_page = QWidget()  # Placeholder, will be replaced when a dataset is opened
        self.visualize_page = VisualizationWidget()
        self.export_page = ExportView(self.status_bar)
        self.settings_page = SettingsView(self.status_bar)
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.datasets_page)
        self.content_stack.addWidget(self.visualize_page)
        self.content_stack.addWidget(self.export_page)
        self.content_stack.addWidget(self.settings_page)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack)
        
        self.setCentralWidget(central_widget)
        
        # Connect signals
        for i, btn in enumerate(self.nav_buttons):
            btn.clicked.connect(lambda checked, idx=i: self.change_page(idx))
        
        # Set initial page
        self.nav_buttons[0].setChecked(True)
        self.content_stack.setCurrentIndex(0)
        
    def change_page(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.content_stack.setCurrentIndex(index)
        
    def open_dataset(self, dataset_path):
        from scripts.dataset_manager import DatasetManager
        
        # Create dataset manager
        dataset_manager = DatasetManager(dataset_path)
        
        # Create dataset view
        dataset_view = DatasetView(dataset_manager, self.status_bar)
        
        # Replace the datasets page
        old_widget = self.content_stack.widget(1)
        self.content_stack.removeWidget(old_widget)
        old_widget.deleteLater()
        
        self.datasets_page = dataset_view
        self.content_stack.insertWidget(1, self.datasets_page)
        
        # Switch to datasets page
        self.change_page(1)
        
        # Update status bar
        self.status_bar.showMessage(f"Dataset loaded: {dataset_path}", 5000)
