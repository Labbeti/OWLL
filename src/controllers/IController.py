from src.views.PieEventObserver import PieEventObserver
from abc import abstractmethod


class IController(PieEventObserver):
    @abstractmethod
    def loadFileModel(self, filepath: str):
        raise Exception("Not implemented")

    @abstractmethod
    def saveFileModel(self, filepath: str):
        raise Exception("Not implemented")

    @abstractmethod
    def getModelParams(self):
        raise Exception("Not implemented")

    @abstractmethod
    def updateModel(self):
        raise Exception("Not implemented")
