
from abc import ABCMeta
from abc import abstractmethod
from ontology.OPCharacteristics import OPCharacteristics


# Interface for Ontology classes.
class AbstractOntology(object, metaclass=ABCMeta):
    __filepath: str = ""

    # Return the name of the OP or class target by the parameter uri.
    @abstractmethod
    def getName(self, uri: str) -> str:
        raise NotImplementedError("user must define getName")

    @abstractmethod
    def getNbErrors(self) -> int:
        raise NotImplementedError("user must define getNbErrors")

    @abstractmethod
    def getObjectProperties(self) -> list:
        raise NotImplementedError("user must define getObjectProperties")

    @abstractmethod
    def getOPCharacteristics(self, opUri: str) -> OPCharacteristics:
        raise NotImplementedError("user must define getOPCharacteristics")

    @abstractmethod
    def getOWLTriples(self) -> list:
        raise NotImplementedError("user must define getTriples")

    @abstractmethod
    def isLoaded(self) -> bool:
        raise NotImplementedError("user must define isLoaded")
