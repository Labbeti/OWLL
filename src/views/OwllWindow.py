from PyQt5.QtWidgets import QMainWindow
from src.controllers.IClusteringController import IClusteringController
from src import PROJECT_VERSION


class OwllWindow(QMainWindow):
    def __init__(self):
        """
            Constructor of OwllWindow.
        """
        QMainWindow.__init__(self)

        self.title = "OWLL GUI " + PROJECT_VERSION
        self.controller = None
        self.initUI()

    def initUI(self):
        """
            Private method for initilize interface.
        """
        self.setWindowTitle(self.title)

    def closeEvent(self, event):
        """
            Method called when close button on window is pushed.
            :param event: event object.
        """
        self.controller.onClose()

    def setController(self, controller: IClusteringController):
        """
            Set the clustering controller of the window.
            :param controller: the clustering controller of the application.
        """
        self.controller = controller
