from abc import abstractmethod


class PieEventObserver:
    @abstractmethod
    def onClusterClick(self, label: str):
        raise Exception("Not implemented")
