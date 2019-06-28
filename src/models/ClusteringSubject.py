from src.models.ClusteringObserver import ClusteringObserver


class ClusteringSubject:
    def __init__(self):
        """
            Constructor of CLusteringSubject.
        """
        self.observers = []

    def addObs(self, obs: ClusteringObserver):
        """
            Add clustering observer to subject.
            :param obs: observer to add.
        """
        self.observers.append(obs)

    def notifyClusteringBegan(self):
        """
            Notify observers that the clustering from OPD process has began.
        """
        for obs in self.observers:
            obs.onClusteringBegan()

    def notifyClusteringEnded(self):
        """
            Notify observers that the clustering from OPD process is ended.
        """
        for obs in self.observers:
            obs.onClusteringEnded()

    def notifyModelLoaded(self):
        """
            Notify observers that the model loading from JSON file is ended.
        """
        for obs in self.observers:
            obs.onModelLoaded()

    def notifySubmitResult(self, centerName: str, nearest: str):
        """
            Notify observers that the OP submitted is classified in the cluster "centerName".
            :param centerName: the center/label of the associated cluster.
            :param nearest: the nearest OP name of the OP submitted.
        """
        for obs in self.observers:
            obs.onSubmitResult(centerName, nearest)
