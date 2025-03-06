# gui/views/settings_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFrame, QCheckBox, QFileDialog, QMessageBox, QLineEdit,
    QFormLayout, QTabWidget, QSpinBox, QColorDialog
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor
import qtawesome as qta
import os
import json


class ColorButton(QPushButton):
    """Button that allows users to select a custom color."""
    
    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self.color = color or QColor("#3498db")
        self.setFixedSize(30, 30)
        self.clicked.connect(self.choose_color)
        self.update_button_color()

    def choose_color(self):
        """Opens a color picker dialog."""
        color = QColorDialog.getColor(self.color, self.parent(), "Choose Color")
        if color.isValid():
            self.color = color
            self.update_button_color()

    def update_button_color(self):
        """Updates button appearance based on selected color."""
        self.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #bdc3c7;")

    def get_color(self):
        return self.color.name()


class SettingsView(QWidget):
    """UI for managing app settings, appearance, and performance options."""

    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.settings = QSettings("Audionomy", "Audionomy")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Initializes the settings UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Settings")
        header.setObjectName("page-header")
        layout.addWidget(header)

        # Tabs for different settings
        self.tabs = QTabWidget()

        # General Settings
        self.general_tab = self.create_general_settings()
        self.tabs.addTab(self.general_tab, "General")

        # Appearance Settings
        self.appearance_tab = self.create_appearance_settings()
        self.tabs.addTab(self.appearance_tab, "Appearance")

        # Performance Settings
        self.performance_tab = self.create_performance_settings()
        self.tabs.addTab(self.performance_tab, "Performance")

        layout.addWidget(self.tabs)

        # Buttons (Reset & Save)
        button_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)

        save_btn = QPushButton(qta.icon("fa5s.save"), "Save Settings")
        save_btn.setObjectName("primary-button")
        save_btn.clicked.connect(self.save_settings)

        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def create_general_settings(self):
        """Creates general settings UI."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Default Dataset Location
        form_layout = QFormLayout()
        self.default_dataset_location = QLineEdit()
        browse_btn = QPushButton(qta.icon("fa5s.folder-open"), "")
        browse_btn.clicked.connect(self.browse_dataset_location)
        location_layout = QHBoxLayout()
        location_layout.addWidget(self.default_dataset_location)
        location_layout.addWidget(browse_btn)
        form_layout.addRow("Default Dataset Location:", location_layout)

        # Audio Settings
        self.default_audio_format = QComboBox()
        self.default_audio_format.addItems(["WAV", "MP3", "FLAC", "OGG"])
        form_layout.addRow("Default Audio Format:", self.default_audio_format)

        self.audio_quality = QComboBox()
        self.audio_quality.addItems(["Low", "Medium", "High", "Lossless"])
        form_layout.addRow("Audio Quality:", self.audio_quality)

        self.normalize_on_import = QCheckBox("Normalize audio on import")
        form_layout.addRow("", self.normalize_on_import)

        layout.addLayout(form_layout)
        return tab

    def create_appearance_settings(self):
        """Creates appearance settings UI."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Theme Selection
        form_layout = QFormLayout()
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark", "System"])
        form_layout.addRow("Theme:", self.theme_selector)

        self.accent_color = ColorButton()
        form_layout.addRow("Accent Color:", self.accent_color)

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 16)
        self.font_size.setValue(11)
        form_layout.addRow("Font Size:", self.font_size)

        layout.addLayout(form_layout)
        return tab

    def create_performance_settings(self):
        """Creates performance settings UI."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Performance Settings
        form_layout = QFormLayout()
        self.cache_size = QSpinBox()
        self.cache_size.setRange(100, 10000)
        self.cache_size.setValue(1000)
        self.cache_size.setSuffix(" MB")
        form_layout.addRow("Cache Size:", self.cache_size)

        self.max_threads = QSpinBox()
        self.max_threads.setRange(1, 16)
        self.max_threads.setValue(4)
        form_layout.addRow("Max Threads:", self.max_threads)

        self.enable_hardware_accel = QCheckBox("Enable hardware acceleration")
        self.enable_hardware_accel.setChecked(True)
        form_layout.addRow("", self.enable_hardware_accel)

        layout.addLayout(form_layout)
        return tab

    def browse_dataset_location(self):
        """Opens file dialog for selecting dataset location."""
        folder = QFileDialog.getExistingDirectory(self, "Select Default Dataset Location")
        if folder:
            self.default_dataset_location.setText(folder)

    def load_settings(self):
        """Loads settings from persistent storage."""
        self.default_dataset_location.setText(
            self.settings.value("default_dataset_location", os.path.expanduser("~/Audionomy/datasets"))
        )
        self.default_audio_format.setCurrentText(self.settings.value("default_audio_format", "WAV"))
        self.audio_quality.setCurrentText(self.settings.value("audio_quality", "High"))
        self.normalize_on_import.setChecked(self.settings.value("normalize_on_import", False, type=bool))

        self.theme_selector.setCurrentText(self.settings.value("theme", "Light"))
        self.accent_color.color = QColor(self.settings.value("accent_color", "#3498db"))
        self.accent_color.update_button_color()
        self.font_size.setValue(self.settings.value("font_size", 11, type=int))

        self.cache_size.setValue(self.settings.value("cache_size", 1000, type=int))
        self.max_threads.setValue(self.settings.value("max_threads", 4, type=int))
        self.enable_hardware_accel.setChecked(self.settings.value("enable_hardware_accel", True, type=bool))

    def save_settings(self):
        """Saves user settings to persistent storage."""
        self.settings.setValue("default_dataset_location", self.default_dataset_location.text())
        self.settings.setValue("default_audio_format", self.default_audio_format.currentText())
        self.settings.setValue("audio_quality", self.audio_quality.currentText())
        self.settings.setValue("normalize_on_import", self.normalize_on_import.isChecked())

        self.settings.setValue("theme", self.theme_selector.currentText())
        self.settings.setValue("accent_color", self.accent_color.get_color())
        self.settings.setValue("font_size", self.font_size.value())

        self.settings.setValue("cache_size", self.cache_size.value())
        self.settings.setValue("max_threads", self.max_threads.value())
        self.settings.setValue("enable_hardware_accel", self.enable_hardware_accel.isChecked())

        self.settings.sync()
        self.status_bar.showMessage("Settings saved successfully", 3000)

    def reset_settings(self):
        """Resets all settings to default values."""
        self.settings.clear()
        self.load_settings()
        self.status_bar.showMessage("Settings reset to defaults", 3000)
