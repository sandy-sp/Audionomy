# gui/main_window.py

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QStackedWidget, QFrame, QStatusBar
)
from PySide6.QtCore import Qt
import qtawesome as qta
from scripts.dataset_manager import DatasetManager
# Import Views
from gui.views.dashboard_view import DashboardWidget
from gui.views.dataset_view import DatasetView
from gui.views.visualization_view import VisualizationWidget
from gui.views.export_view import ExportView
from gui.views.settings_view import SettingsView

class ModernMainWindow(QMainWindow):
    """Main Application Window with Sidebar Navigation and Dynamic Content Switching"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audionomy")
        self.setWindowIcon(qta.icon('fa5s.headphones-alt'))
        self.resize(1200, 800)

        # Initialize Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Welcome to Audionomy")

        # Ensure dataset manager is initialized **before** passing it to `VisualizationWidget`
        self.dataset_manager = DatasetManager("datasets")

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the main layout, sidebar, and content area."""
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        self.setCentralWidget(central_widget)

        # Initialize Pages
        self.initialize_pages()

        # Set default page
        self.switch_page(0)

    def initialize_pages(self):
        """Initialize application pages and add them to the stacked widget."""
        self.dashboard_page = DashboardWidget(self.status_bar)
        self.dashboard_page.datasetSelected.connect(self.open_dataset)

        self.datasets_page = QWidget()  # Placeholder for dataset views

        # ✅ Pass `dataset_manager` when initializing `VisualizationWidget`
        self.visualization_page = VisualizationWidget(dataset_manager=self.dataset_manager)

        self.export_page = ExportView(self.status_bar)
        self.settings_page = SettingsView(self.status_bar)

        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.datasets_page)
        self.content_stack.addWidget(self.visualization_page)
        self.content_stack.addWidget(self.export_page)
        self.content_stack.addWidget(self.settings_page)

    def create_sidebar(self):
        """Creates the sidebar with navigation buttons."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)  # Adjust sidebar width
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)

        # App Logo
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

        # Navigation Buttons
        self.nav_buttons = []
        nav_items = [
            ("dashboard", "Dashboard", "fa5s.home"),
            ("datasets", "Datasets", "fa5s.database"),
            ("visualize", "Visualize", "fa5s.chart-bar"),
            ("export", "Export", "fa5s.file-export"),
            ("settings", "Settings", "fa5s.cog"),
        ]

        for index, (name, label, icon) in enumerate(nav_items):
            btn = QPushButton(qta.icon(icon, color="#ffffff"), f" {label}")
            btn.setObjectName(f"nav-{name}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()  # Pushes buttons up for better layout
        return sidebar

    def switch_page(self, index):
        """Switches to the selected page."""
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.content_stack.setCurrentIndex(index)

    def open_dataset(self, dataset_path):
        """Loads a dataset and switches to the dataset view."""
        from scripts.dataset_manager import DatasetManager

        dataset_manager = DatasetManager(dataset_path)
        dataset_view = DatasetView(dataset_manager, self.status_bar)

        # Replace the datasets page
        old_widget = self.content_stack.widget(1)
        self.content_stack.removeWidget(old_widget)
        old_widget.deleteLater()

        self.datasets_page = dataset_view
        self.content_stack.insertWidget(1, self.datasets_page)

        self.switch_page(1)  # Navigate to dataset view
        self.status_bar.showMessage(f"Dataset loaded: {dataset_path}", 5000)
