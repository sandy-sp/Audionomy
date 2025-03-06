import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
from PySide6.QtGui import QIcon
import qtawesome as qta
from views.home import HomeView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audionomy")
        self.setWindowIcon(qta.icon('fa5s.music'))

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.home_view = HomeView(self.status_bar)
        self.setCentralWidget(self.home_view)
        self.resize(800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
