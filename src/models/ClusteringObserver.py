from abc import abstractmethod


class ClusteringObserver:
    @abstractmethod
    def onClusteringEnded(self):
        raise Exception("Not implemented")

    @abstractmethod
    def onModelLoaded(self):
        raise Exception("Not implemented")
