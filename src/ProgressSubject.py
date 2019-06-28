from PyQt5.QtWidgets import QMessageBox
from src.ProgressObserver import ProgressObserver


class ProgressSubject:
    """
        Design pattern subject-observer.
    """

    def __init__(self):
        """
            Constructor of ProgressSubject.
        """
        self.progressObservers = []
        self.currentProgress = 0
        self.maxProgress = 1

    def addProgressObs(self, obs: ProgressObserver):
        """
            Add an observer to the progress subject.
            :param obs: The observer to add.
        """
        self.progressObservers.append(obs)

    def notifyProgress(self, stepName: str, progress: float):
        """
            Update all observers with the current status.
            :param stepName: The name of the current step.
            :param progress: The value in [0,1] of the current progress.
        """
        for obs in self.progressObservers:
            obs.onProgress(stepName, progress)

    def getProgressProportion(self) -> float:
        """
            Return the current progress proportion in [0,1].
        """
        return self.currentProgress / self.maxProgress

    def incrProgress(self, step: str):
        """
            Increment the current integer progress value by 1 and update progress to observers.
            :param step: The name of the current step.
        """
        self.currentProgress += 1
        self.notifyProgress(step, self.getProgressProportion())

    def resetProgress(self, maxProgress: int):
        """
            Reset the current progress to 0 and set the maxProgress.
            :param maxProgress: The new value for maxProgress.
        """
        self.currentProgress = 0
        self.maxProgress = maxProgress

    def notifyError(self, message: str):
        """
            Update all observers when the progress is aborted and show an error dialog box message.
            :param message: The error message to show.
        """
        for obs in self.progressObservers:
            obs.onProgressAbort()
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setIcon(QMessageBox.Information)
        box.setText(message)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()
