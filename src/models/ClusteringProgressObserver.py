from abc import abstractmethod


class ClusteringProgressObserver:
    @abstractmethod
    def onProgress(self, stepName: str, percent: int):
        raise Exception("Not implemented.")
