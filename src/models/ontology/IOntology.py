from abc import ABCMeta
from abc import abstractmethod
from src.models.ontology import OpData

"""
                        IOntology
                            ^
                            |
            +---------------+---------------+
            |                               |
            |                               |
        Ontology                     AbstractOntology
                                            ^
                                            |
                                +-----------+-----------+
                                |                       |
                                |                       |
                        OwlreadyOntology          RdflibOntology
"""


class IOntology(object, metaclass=ABCMeta):
    """
        Interface for Ontology classes.
    """

    @abstractmethod
    def getAllClsData(self) -> dict:
        """
            Return the list of ClsData.
            :return:
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getAllOpsData(self) -> dict:
        """
            Return the list of OpData.
            :return:
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getClsData(self, clsIri: str) -> str:
        """
            Return the properties of a class.
            :param clsIri:
            :return:
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getFilepath(self) -> str:
        """
            Get the filepath of the ontology file loaded.
            :return:
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getOpName(self, iri: str) -> str:
        """
            Return the name of the OP or class target by the parameter uri.
            :param iri:
            :return:
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getNbErrors(self) -> int:
        """
            Return the number of errors encountered during loading of the ontology.
            :return:
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getOpNames(self) -> list:
        """
            Return the list of object properties names.
            :return:
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getOpData(self, opUri: str) -> OpData:
        """
            Return the properties of an OP.
            :param opUri:
            :return:
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def isLoaded(self) -> bool:
        """
            Return True if is loading is succesfull.
            :return:
        """
        raise NotImplementedError("Abstract method")
