from PyQt5.QtWidgets import QProgressDialog, QApplication
from PyQt5.QtCore import Qt
from src.models.ClusteringObserver import ClusteringObserver


class ProgressView(ClusteringObserver):
    def __init__(self, app: QApplication):
        self.app = app
        self.progressBar = QProgressDialog()

        self.initUI()

    def initUI(self):
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
        self.progressBar.show()

    def onClusteringEnded(self):
        self.progressBar.hide()

    def onModelLoaded(self):
        pass

    def onProgress(self, stepName: str, value: float):
        self.progressBar.setLabelText(stepName)
        barValue = int(value * (self.progressBar.maximum() - self.progressBar.minimum()))
        self.progressBar.setValue(barValue)
        self.app.processEvents()
