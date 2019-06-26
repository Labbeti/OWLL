from src.models.ClusteringParameters import ClusteringParameters
from src.controllers.PieEventObserver import PieEventObserver
from abc import abstractmethod


class IClusteringController(PieEventObserver):
    @abstractmethod
    def updateModel(self):
        """
            Update the clustering model with the current parameters coming from views.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def submitOpToModel(self, opName: str, domain: str, range_: str, mathProps: dict):
        """
            Call model for submit a Object Property from InputView.
            :param opName: The OP name.
            :param domain: The OP domain.
            :param range_: The OP range.
            :param mathProps: A dict of string keys and boolean values which contains the math properties submitted.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onClose(self):
        """
            Close the window.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getModelParams(self) -> ClusteringParameters:
        """
            Ask to the model the current parameters.
            :return: The model parameters.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getModelClusters(self) -> list:
        """
            Ask to the model the current clusters names.
            :return: The model clusters names as a string list list.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getModelCenters(self) -> list:
        """
            Ask to the model the current centers names.
            :return: The model centers as a string list.
        """
        raise NotImplementedError("Abstract method")
