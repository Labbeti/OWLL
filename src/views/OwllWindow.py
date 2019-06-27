from PyQt5.QtWidgets import QMainWindow
from src.controllers.IClusteringController import IClusteringController
from src import PROJECT_VERSION


class OwllWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # Init attributes
        self.title = "OWLL GUI " + PROJECT_VERSION
        self.controller = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

    def closeEvent(self, event):
        self.controller.onClose()

    def setController(self, controller: IClusteringController):
        self.controller = controller
