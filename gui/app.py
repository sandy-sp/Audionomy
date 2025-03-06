# gui/app.py

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream, QSettings
from gui.main_window import ModernMainWindow


class AudionomyApp(QApplication):
    """Main application class to manage startup, theming, and error handling."""

    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Audionomy")
        self.settings = QSettings("Audionomy", "Audionomy")
        
        # Load Theme
        self.load_theme()

        # Load & Apply Stylesheet
        self.apply_stylesheet()

    def load_theme(self):
        """Loads the user-selected theme from settings."""
        theme = self.settings.value("theme", "Light")
        if theme == "Dark":
            self.setStyle("Fusion")
        elif theme == "Light":
            self.setStyle("Windows")

    def apply_stylesheet(self):
        """Applies the stylesheet from the resources folder."""
        style_file = QFile("gui/resources/style.qss")
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())

    def handle_exception(self, exc_type, exc_value, traceback):
        """Global exception handler to log unexpected errors."""
        logger.critical(f"Unexpected error: {exc_type.__name__}: {exc_value}")


def main():
    """Main entry point for launching the Audionomy application."""
    app = AudionomyApp(sys.argv)

    # Set up error handling
    sys.excepthook = app.handle_exception

    # Create and show main window
    window = ModernMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
