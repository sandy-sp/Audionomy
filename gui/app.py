# gui/app.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from views.home import HomeView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.home_view = HomeView()  # Instantiate HomeView
        self.setCentralWidget(self.home_view)  # Fixed here: removed parentheses

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Audionomy")
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())
