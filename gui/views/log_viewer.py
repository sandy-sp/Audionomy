# gui/views/log_viewer.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QLabel,
    QHBoxLayout, QComboBox, QLineEdit
)
from PySide6.QtCore import QFileSystemWatcher, Qt
import os
import re

LOG_FILE = "logs/audionomy.log"


class LogViewer(QWidget):
    """A real-time log viewer for monitoring Audionomy logs with filtering and search."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Real-Time Log Viewer")
        self.resize(800, 500)

        self.setup_ui()
        self.setup_log_watcher()

    def setup_ui(self):
        """Initializes the log viewer UI."""
        layout = QVBoxLayout(self)

        # Log Display Area
        self.log_display = QPlainTextEdit()
        self.log_display.setReadOnly(True)
        
        # Fix: Use setFont() instead of setFontFamily()
        font = self.log_display.font()
        font.setFamily("Courier")
        self.log_display.setFont(font)

        layout.addWidget(self.log_display)
        self.setLayout(layout)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("🔍 Real-Time Logs")
        header_label.setObjectName("page-header")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Log Level Filter
        self.log_filter = QComboBox()
        self.log_filter.addItems(["All", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_filter.currentIndexChanged.connect(self.load_logs)
        header_layout.addWidget(self.log_filter)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔎 Search logs...")
        self.search_input.textChanged.connect(self.load_logs)
        header_layout.addWidget(self.search_input)

        # Clear Logs Button
        self.clear_button = QPushButton("🗑 Clear Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.clear_button)

        layout.addLayout(header_layout)

        # Log Display Area
        self.log_display = QPlainTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFontFamily("Courier")
        self.log_display.setWordWrapMode(False)
        layout.addWidget(self.log_display)

        # Load initial logs
        self.load_logs()

    def setup_log_watcher(self):
        """Sets up a file system watcher to monitor log changes."""
        self.log_watcher = QFileSystemWatcher([LOG_FILE])
        self.log_watcher.fileChanged.connect(self.load_logs)

    def load_logs(self):
        """Loads and filters the latest log file contents with search functionality."""
        if not os.path.exists(LOG_FILE):
            self.log_display.setPlainText("No logs found.")
            return

        selected_level = self.log_filter.currentText()
        search_query = self.search_input.text().strip().lower()

        with open(LOG_FILE, "r") as f:
            logs = f.readlines()

        filtered_logs = self.filter_logs(logs, selected_level, search_query)
        self.log_display.setPlainText("".join(filtered_logs))

    def filter_logs(self, logs, level, search_query):
        """Filters logs based on the selected log level and search query."""
        if level == "All" and not search_query:
            return logs  # No filtering needed

        filtered_logs = []
        level_pattern = re.compile(f" - {level} - ") if level != "All" else None

        for log in logs:
            if (not level_pattern or level_pattern.search(log)) and (not search_query or search_query in log.lower()):
                filtered_logs.append(log)

        return filtered_logs

    def clear_logs(self):
        """Clears the log file and updates the display."""
        with open(LOG_FILE, "w") as f:
            f.truncate(0)

        self.log_display.setPlainText("")
