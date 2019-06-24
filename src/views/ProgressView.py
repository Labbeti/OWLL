from PyQt5.QtWidgets import QWidget, QProgressDialog
from src.models.ClusteringProgressObserver import ClusteringProgressObserver
from src.util import dbg


class ProgressView(ClusteringProgressObserver):
    def __init__(self):
        self.progress = None

    def onProgress(self, stepName: str, percent: int):
        dbg("onProgress = ", self.progress, stepName, percent)
        if self.progress is None:
            self.progress = QProgressDialog()
            self.progress.setMinimum(0)
            self.progress.setMaximum(100)
            self.progress.setMinimumSize(300, 200)

        self.progress.setWindowTitle(stepName)
        self.progress.setValue(percent)

        if percent >= 100:
            self.progress.close()
            self.progress = None
