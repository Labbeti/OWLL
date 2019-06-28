from src.controllers.OpdObserver import OpdObserver


class OpdSubject:
    """
        Design Pattern subject-observer.
    """

    def __init__(self):
        """
            Constructor of OpdSubject.
        """
        self.observers = []

    def addOpdObs(self, obs: OpdObserver):
        """
            Add an observer to the opd subject.
            :param obs: observer to add.
        """
        self.observers.append(obs)

    def notifyOpdLoadBegan(self):
        """
            Notify each observer that OPD is empty and the load of OPD will begin.
        """
        for obs in self.observers:
            obs.onOpdLoadBegan()

    def notifyOpdLoadEnded(self):
        """
            Notify each observer that load of OPD is over, but not if it was successfull.
        """
        for obs in self.observers:
            obs.onOpdLoadEnded()
