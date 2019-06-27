from abc import abstractmethod


class ProgressObserver:
    @abstractmethod
    def onProgress(self, stepName: str, progress: float):
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onProgressAbort(self):
        raise NotImplementedError("Abstract method")
