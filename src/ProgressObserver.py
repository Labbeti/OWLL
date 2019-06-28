from abc import abstractmethod


class ProgressObserver:
    @abstractmethod
    def onProgress(self, stepName: str, progress: float):
        """
            Method called when the progress must be updated.
            :param stepName: The name of the current step.
            :param progress: The value in [0,1] of the current progress.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onProgressAbort(self):
        """
            Method called when the progress is aborted.
        """
        raise NotImplementedError("Abstract method")
