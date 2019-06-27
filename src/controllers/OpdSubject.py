from src.controllers.OpdObserver import OpdObserver


class OpdSubject:
    def __init__(self):
        self.observers = []

    def addOpdObs(self, obs: OpdObserver):
        self.observers.append(obs)

    def notifyOpdLoadBegan(self):
        for obs in self.observers:
            obs.onOpdLoadBegan()

    def notifyOpdLoadEnded(self):
        for obs in self.observers:
            obs.onOpdLoadEnded()
