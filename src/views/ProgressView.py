from PyQt5.QtWidgets import QProgressDialog, QApplication
from PyQt5.QtCore import Qt
from src.models.ClusteringObserver import ClusteringObserver
from src.controllers.OpdObserver import OpdObserver
from src.ProgressObserver import ProgressObserver


class ProgressView(ClusteringObserver, ProgressObserver, OpdObserver):
    def __init__(self, app: QApplication):
        """
            Constructor of ProgressView.
            :param app: The PyQt application object.
        """
        self.app = app
        self.progressBar = QProgressDialog()

        self.initUI()

    def initUI(self):
        """
            Private method for initialize interface.
        """
        self.progressBar.close()
        self.progressBar.setAutoClose(False)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setMinimumSize(400, 100)
        self.progressBar.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.progressBar.setWindowTitle("Updating model...")
        self.progressBar.setCancelButton(None)

    def onClusteringBegan(self):
        """
            Override
        """
        self.progressBar.show()

    def onClusteringEnded(self):
        """
            Override
        """
        self.progressBar.hide()

    def onModelLoaded(self):
        """
            Override
        """
        pass

    def onProgress(self, stepName: str, progress: float):
        """
            Override
        """
        self.progressBar.setLabelText(stepName)
        barValue = int(progress * (self.progressBar.maximum() - self.progressBar.minimum()))
        self.progressBar.setValue(barValue)
        self.app.processEvents()

    def onProgressAbort(self):
        """
            Override
        """
        self.progressBar.hide()

    def onOpdLoadBegan(self):
        """
            Override
        """
        self.progressBar.show()

    def onOpdLoadEnded(self):
        """
            Override
        """
        self.progressBar.hide()
