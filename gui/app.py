import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from views.home import HomeView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.home_view = HomeView()
        self.setCentralWidget(self.home_view)
        self.setWindowTitle("Audionomy - Audio Dataset Manager")
        self.resize(1024, 768)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
