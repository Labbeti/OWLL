from src.models.ClusteringObserver import ClusteringObserver


class ClusteringSubject:
    def __init__(self):
        self.observers = []

    def addObs(self, obs: ClusteringObserver):
        self.observers.append(obs)

    def notifyClusteringEnded(self):
        for obs in self.observers:
            obs.onClusteringEnded()

    def notifyModelLoaded(self):
        for obs in self.observers:
            obs.onModelLoaded()
