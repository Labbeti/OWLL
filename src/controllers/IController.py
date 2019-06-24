from src.models.ClusteringParameters import ClusteringParameters
from src.controllers.PieEventObserver import PieEventObserver
from abc import abstractmethod


class IController(PieEventObserver):
    @abstractmethod
    def updateModel(self):
        raise Exception("Not implemented")

    @abstractmethod
    def onClose(self):
        raise Exception("Not implemented")

    @abstractmethod
    def onOpenModel(self):
        raise Exception("Not implemented")

    @abstractmethod
    def onSaveModel(self):
        raise Exception("Not implemented")

    @abstractmethod
    def getModelParams(self) -> ClusteringParameters:
        raise Exception("Not implemented")

    @abstractmethod
    def getModelClusters(self) -> list:
        raise Exception("Not implemented")

    @abstractmethod
    def getModelCenters(self) -> list:
        raise Exception("Not implemented")
