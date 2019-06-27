from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from src.controllers.IClusteringController import IClusteringController


class OwllWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # Init attributes
        self.title = 'OWLL-GUI'
        self.controller = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

    def closeEvent(self, event):
        self.controller.onClose()

    def setController(self, controller: IClusteringController):
        self.controller = controller
