# gui/views/settings_view.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFrame, QGridLayout, QCheckBox, QFileDialog, QMessageBox, QLineEdit,
    QFormLayout, QTabWidget, QSpinBox, QColorDialog
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor
import qtawesome as qta
import os
import json

class ColorButton(QPushButton):
    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self.color = color or QColor("#3498db")
        self.setFixedSize(30, 30)
        self.clicked.connect(self.choose_color)
        self.update_button_color()
        
    def choose_color(self):
        color = QColorDialog.getColor(self.color, self.parent(), "Choose Color")
        if color.isValid():
            self.color = color
            self.update_button_color()
            
    def update_button_color(self):
        self.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #bdc3c7;")
        
    def get_color(self):
        return self.color.name()

class SettingsView(QWidget):
    def __init__(self, status_bar, parent=None):
        super().__init__(parent)
        self.status_bar = status_bar
        self.settings = QSettings("Audionomy", "Audionomy")
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Settings")
        header.setObjectName("page-header")
        layout.addWidget(header)
        
        # Settings tabs
        self.tabs = QTabWidget()
        
        # General settings tab
        self.general_tab = QWidget()
        general_layout = QVBoxLayout(self.general_tab)
        
        # Application settings
        app_frame = QFrame()
        app_frame.setObjectName("section-frame")
        app_layout = QVBoxLayout(app_frame)
        app_layout.addWidget(QLabel("Application Settings"))
        
        form_layout = QFormLayout()
        
        self.default_dataset_location = QLineEdit()
        browse_btn = QPushButton(qta.icon("fa5s.folder-open"), "")
        browse_btn.clicked.connect(self.browse_dataset_location)
        location_layout = QHBoxLayout()
        location_layout.addWidget(self.default_dataset_location)
        location_layout.addWidget(browse_btn)
        form_layout.addRow("Default Dataset Location:", location_layout)
        
        self.auto_save = QCheckBox("Auto-save changes")
        self.auto_save.setChecked(True)
        form_layout.addRow("", self.auto_save)
        
        self.confirm_delete = QCheckBox("Confirm before deleting")
        self.confirm_delete.setChecked(True)
        form_layout.addRow("", self.confirm_delete)
        
        app_layout.addLayout(form_layout)
        general_layout.addWidget(app_frame)
        
        # Audio settings
        audio_frame = QFrame()
        audio_frame.setObjectName("section-frame")
        audio_layout = QVBoxLayout(audio_frame)
        audio_layout.addWidget(QLabel("Audio Settings"))
        
        audio_form = QFormLayout()
        
        self.default_audio_format = QComboBox()
        self.default_audio_format.addItems(["WAV", "MP3", "FLAC", "OGG"])
        audio_form.addRow("Default Audio Format:", self.default_audio_format)
        
        self.audio_quality = QComboBox()
        self.audio_quality.addItems(["Low", "Medium", "High", "Lossless"])
        audio_form.addRow("Audio Quality:", self.audio_quality)
        
        self.normalize_on_import = QCheckBox("Normalize audio on import")
        audio_form.addRow("", self.normalize_on_import)
        
        audio_layout.addLayout(audio_form)
        general_layout.addWidget(audio_frame)
        
        # Appearance tab
        self.appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(self.appearance_tab)
        
        # Theme settings
        theme_frame = QFrame()
        theme_frame.setObjectName("section-frame")
        theme_layout = QVBoxLayout(theme_frame)
        theme_layout.addWidget(QLabel("Theme Settings"))
        
        theme_form = QFormLayout()
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark", "System"])
        theme_form.addRow("Theme:", self.theme_selector)
        
        self.accent_color = ColorButton()
        theme_form.addRow("Accent Color:", self.accent_color)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 16)
        self.font_size.setValue(11)
        theme_form.addRow("Font Size:", self.font_size)
        
        theme_layout.addLayout(theme_form)
        appearance_layout.addWidget(theme_frame)
        
        # UI settings
        ui_frame = QFrame()
        ui_frame.setObjectName("section-frame")
        ui_layout = QVBoxLayout(ui_frame)
        ui_layout.addWidget(QLabel("UI Settings"))
        
        ui_form = QFormLayout()
        
        self.show_tooltips = QCheckBox("Show tooltips")
        self.show_tooltips.setChecked(True)
        ui_form.addRow("", self.show_tooltips)
        
        self.show_status_bar = QCheckBox("Show status bar")
        self.show_status_bar.setChecked(True)
        ui_form.addRow("", self.show_status_bar)
        
        self.compact_mode = QCheckBox("Compact mode")
        ui_form.addRow("", self.compact_mode)
        
        ui_layout.addLayout(ui_form)
        appearance_layout.addWidget(ui_frame)
        
        # Advanced tab
        self.advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(self.advanced_tab)
        
        # Performance settings
        perf_frame = QFrame()
        perf_frame.setObjectName("section-frame")
        perf_layout = QVBoxLayout(perf_frame)
        perf_layout.addWidget(QLabel("Performance Settings"))
        
        perf_form = QFormLayout()
        
        self.cache_size = QSpinBox()
        self.cache_size.setRange(100, 10000)
        self.cache_size.setValue(1000)
        self.cache_size.setSuffix(" MB")
        perf_form.addRow("Cache Size:", self.cache_size)
        
        self.max_threads = QSpinBox()
        self.max_threads.setRange(1, 16)
        self.max_threads.setValue(4)
        perf_form.addRow("Max Threads:", self.max_threads)
        
        self.enable_hardware_accel = QCheckBox("Enable hardware acceleration")
        self.enable_hardware_accel.setChecked(True)
        perf_form.addRow("", self.enable_hardware_accel)
        
        perf_layout.addLayout(perf_form)
        advanced_layout.addWidget(perf_frame)
        
        # Developer settings
        dev_frame = QFrame()
        dev_frame.setObjectName("section-frame")
        dev_layout = QVBoxLayout(dev_frame)
        dev_layout.addWidget(QLabel("Developer Settings"))
        
        dev_form = QFormLayout()
        
        self.debug_mode = QCheckBox("Debug mode")
        dev_form.addRow("", self.debug_mode)
        
        self.log_level = QComboBox()
        self.log_level.addItems(["Error", "Warning", "Info", "Debug"])
        dev_form.addRow("Log Level:", self.log_level)
        
        dev_layout.addLayout(dev_form)
        advanced_layout.addWidget(dev_frame)
        
        # Add tabs
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.appearance_tab, "Appearance")
        self.tabs.addTab(self.advanced_tab, "Advanced")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        
        save_btn = QPushButton(qta.icon("fa5s.save"), "Save Settings")
        save_btn.setObjectName("primary-button")
        save_btn.clicked.connect(self.save_settings)
        
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
    def browse_dataset_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Default Dataset Location")
        if folder:
            self.default_dataset_location.setText(folder)
            
    def load_settings(self):
        # General settings
        self.default_dataset_location.setText(
            self.settings.value("default_dataset_location", 
                               os.path.join(os.path.expanduser("~"), "Audionomy", "datasets"))
        )
        self.auto_save.setChecked(self.settings.value("auto_save", True, type=bool))
        self.confirm_delete.setChecked(self.settings.value("confirm_delete", True, type=bool))
        
        # Audio settings
        self.default_audio_format.setCurrentText(self.settings.value("default_audio_format", "WAV"))
        self.audio_quality.setCurrentText(self.settings.value("audio_quality", "High"))
        self.normalize_on_import.setChecked(self.settings.value("normalize_on_import", False, type=bool))
        
        # Appearance settings
        self.theme_selector.setCurrentText(self.settings.value("theme", "Light"))
        self.accent_color.color = QColor(self.settings.value("accent_color", "#3498db"))
        self.accent_color.update_button_color()
        self.font_size.setValue(self.settings.value("font_size", 11, type=int))
        
        # UI settings
        self.show_tooltips.setChecked(self.settings.value("show_tooltips", True, type=bool))
        self.show_status_bar.setChecked(self.settings.value("show_status_bar", True, type=bool))
        self.compact_mode.setChecked(self.settings.value("compact_mode", False, type=bool))
        
        # Advanced settings
        self.cache_size.setValue(self.settings.value("cache_size", 1000, type=int))
        self.max_threads.setValue(self.settings.value("max_threads", 4, type=int))
        self.enable_hardware_accel.setChecked(self.settings.value("enable_hardware_accel", True, type=bool))
        
        # Developer settings
        self.debug_mode.setChecked(self.settings.value("debug_mode", False, type=bool))
        self.log_level.setCurrentText(self.settings.value("log_level", "Warning"))
        
    def save_settings(self):
        # General settings
        self.settings.setValue("default_dataset_location", self.default_dataset_location.text())
        self.settings.setValue("auto_save", self.auto_save.isChecked())
        self.settings.setValue("confirm_delete", self.confirm_delete.isChecked())
        
        # Audio settings
        self.settings.setValue("default_audio_format", self.default_audio_format.currentText())
        self.settings.setValue("audio_quality", self.audio_quality.currentText())
        self.settings.setValue("normalize_on_import", self.normalize_on_import.isChecked())
        
        # Appearance settings
        self.settings.setValue("theme", self.theme_selector.currentText())
        self.settings.setValue("accent_color", self.accent_color.get_color())
        self.settings.setValue("font_size", self.font_size.value())
        
        # UI settings
        self.settings.setValue("show_tooltips", self.show_tooltips.isChecked())
        self.settings.setValue("show_status_bar", self.show_status_bar.isChecked())
        self.settings.setValue("compact_mode", self.compact_mode.isChecked())
        
        # Advanced settings
        self.settings.setValue("cache_size", self.cache_size.value())
        self.settings.setValue("max_threads", self.max_threads.value())
        self.settings.setValue("enable_hardware_accel", self.enable_hardware_accel.isChecked())
        
        # Developer settings
        self.settings.setValue("debug_mode", self.debug_mode.isChecked())
        self.settings.setValue("log_level", self.log_level.currentText())
        
        self.settings.sync()
        self.status_bar.showMessage("Settings saved successfully", 3000)
        
        # Notify user that some settings require restart
        QMessageBox.information(self, "Settings Saved", 
                              "Some settings may require restarting the application to take effect.")
        
    def reset_settings(self):
        reply = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings.clear()
            self.load_settings()
            self.status_bar.showMessage("Settings reset to defaults", 3000)
