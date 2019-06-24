from PyQt5.QtWidgets import QMainWindow, QAction
from src.controllers.IController import IController
from src.util import dbg


class OwllWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Init attributes
        self.title = 'OWLL'
        self.controller = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

    def closeEvent(self, event):
        self.controller.onClose()

    def setController(self, controller: IController):
        self.controller = controller
