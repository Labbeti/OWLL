from abc import abstractmethod


class PieEventObserver:
    @abstractmethod
    def onClick(self, label: str):
        raise Exception("Not implemented")
