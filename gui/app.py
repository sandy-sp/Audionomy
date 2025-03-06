# gui/app.py

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream
from gui.main_window import ModernMainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Audionomy")
    
    # Set app style
    app.setStyle("Fusion")
    
    # Load and apply stylesheet
    style_file = QFile("gui/resources/style.qss")
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
    
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
