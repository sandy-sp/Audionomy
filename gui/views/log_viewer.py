# gui/views/log_viewer.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QLabel,
    QHBoxLayout, QComboBox
)
from PySide6.QtCore import QFileSystemWatcher, Qt
import os
import re

LOG_FILE = "logs/audionomy.log"


class LogViewer(QWidget):
    """A real-time log viewer for monitoring Audionomy logs with filtering."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Real-Time Log Viewer")
        self.resize(800, 500)

        self.setup_ui()
        self.setup_log_watcher()

    def setup_ui(self):
        """Initializes the log viewer UI."""
        layout = QVBoxLayout(self)

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
        """Loads and filters logs, applying color coding for log levels."""
        if not os.path.exists(LOG_FILE):
            self.log_display.setPlainText("No logs found.")
            return

        selected_level = self.log_filter.currentText()

        with open(LOG_FILE, "r") as f:
            logs = f.readlines()

        filtered_logs = self.filter_logs(logs, selected_level)

        # Apply color coding
        formatted_logs = ""
        for log in filtered_logs:
            if " - ERROR - " in log:
                log = f'<span style="color:red;">{log}</span>'
            elif " - WARNING - " in log:
                log = f'<span style="color:orange;">{log}</span>'
            elif " - INFO - " in log:
                log = f'<span style="color:blue;">{log}</span>'
            elif " - CRITICAL - " in log:
                log = f'<span style="color:darkred; font-weight:bold;">{log}</span>'

            formatted_logs += log

        self.log_display.setHtml(f"<pre>{formatted_logs}</pre>")

    def filter_logs(self, logs, level):
        """Filters logs based on the selected log level."""
        if level == "All":
            return logs

        filtered_logs = []
        pattern = re.compile(f" - {level} - ")  # Example: " - ERROR - "
        for log in logs:
            if pattern.search(log):
                filtered_logs.append(log)

        return filtered_logs

    def clear_logs(self):
        """Clears the log file and updates the display."""
        with open(LOG_FILE, "w") as f:
            f.truncate(0)

        self.log_display.setPlainText("")
