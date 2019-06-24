from src.models.ClusteringProgressObserver import ClusteringProgressObserver


class ClusteringProgressSubject:
    def __init__(self):
        self.progressObservers = []

    def addProgressObs(self, obs: ClusteringProgressObserver):
        self.progressObservers.append(obs)

    def notifyProgress(self, stepName: str, percent: int):
        for obs in self.progressObservers:
            obs.onProgress(stepName, percent)
