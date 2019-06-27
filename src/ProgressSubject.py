from PyQt5.QtWidgets import QMessageBox
from src.ProgressObserver import ProgressObserver


class ProgressSubject:
    def __init__(self):
        self.progressObservers = []
        self.currentProgress = 0
        self.maxProgress = 1

    def addProgressObs(self, obs: ProgressObserver):
        self.progressObservers.append(obs)

    def notifyProgress(self, stepName: str, progress: float):
        for obs in self.progressObservers:
            obs.onProgress(stepName, progress)

    def getProgressProportion(self) -> float:
        return self.currentProgress / self.maxProgress

    def incrProgress(self, step: str):
        self.currentProgress += 1
        self.notifyProgress(step, self.getProgressProportion())

    def resetProgress(self, maxProgress: int):
        self.currentProgress = 0
        self.maxProgress = maxProgress

    def notifyError(self, message: str):
        for obs in self.progressObservers:
            obs.onProgressAbort()
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setIcon(QMessageBox.Information)
        box.setText(message)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()
