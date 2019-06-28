from abc import abstractmethod


class ClusteringObserver:
    @abstractmethod
    def onClusteringBegan(self):
        """
            Method called when clusterisation from OPD is beginning.
        """
        raise Exception("Abstract method")

    @abstractmethod
    def onClusteringEnded(self):
        """
            Method called when clusterisation from OPD is ended.
        """
        raise Exception("Abstract method")

    @abstractmethod
    def onModelLoaded(self):
        """
            Method called when model loading from JSON file is ended.
        """
        raise Exception("Abstract method")

    def onProgress(self, stepName: str, value: float):
        """
            Update the clusterisation progress view.
            :param stepName: Name of the current step.
            :param value: Value in [0..1] which represent the current progress.
        """
        pass

    def onSubmitResult(self, centerName: str, nearest: str):
        """
            Method called when an OP submitted by user has been classified.
            :param centerName: center/label of the cluster
            :param nearest: Name of the nearest OP name for the OP submitted.
        """
        pass
