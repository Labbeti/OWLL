from abc import abstractmethod


class ClusteringObserver:
    @abstractmethod
    def onClusteringBegan(self):
        raise Exception("Abstract method")

    @abstractmethod
    def onClusteringEnded(self):
        raise Exception("Abstract method")

    @abstractmethod
    def onModelLoaded(self):
        raise Exception("Abstract method")

    def onProgress(self, stepName: str, value: float):
        """
            Update the clusterisation progress view.
            :param stepName: Name of the current step.
            :param value: Value in [0..1] which represent the current progress.
        """
        pass

    def onSubmitResult(self, centerName: str, nearest: str):
        pass
