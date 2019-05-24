
from abc import ABCMeta
from abc import abstractmethod


class AbstractOntology(object, metaclass=ABCMeta):
    __filepath: str = ""

    @abstractmethod
    def getNbErrors(self) -> int:
        raise NotImplementedError("user must define getObjectProperties")

    @abstractmethod
    def getObjectProperties(self) -> list:
        raise NotImplementedError("user must define getObjectProperties")

    @abstractmethod
    def getOWLTriples(self) -> list:
        raise NotImplementedError("user must define getTriples")

    @abstractmethod
    def isLoaded(self) -> bool:
        raise NotImplementedError("user must define isLoaded")
