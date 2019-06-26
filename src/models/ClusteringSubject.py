from src.models.ClusteringObserver import ClusteringObserver


class ClusteringSubject:
    def __init__(self):
        self.observers = []

    def addObs(self, obs: ClusteringObserver):
        self.observers.append(obs)

    def notifyClusteringBegan(self):
        for obs in self.observers:
            obs.onClusteringBegan()

    def notifyClusteringEnded(self):
        for obs in self.observers:
            obs.onClusteringEnded()

    def notifyModelLoaded(self):
        for obs in self.observers:
            obs.onModelLoaded()

    def notifyProgress(self, stepName: str, value: float):
        for obs in self.observers:
            obs.onProgress(stepName, value)

    def notifySubmitResult(self, centerName: str, nearest: str):
        for obs in self.observers:
            obs.onSubmitResult(centerName, nearest)
