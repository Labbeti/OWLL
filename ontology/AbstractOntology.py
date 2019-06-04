
from abc import abstractmethod
from ontology.ClsProperties import ClsProperties
from ontology.IOntology import IOntology
from ontology.OpProperties import OpProperties


# Abstract Ontology for implementation with librairies.
class AbstractOntology(IOntology):
    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str):
        self._filepath = filepath
        self._loaded = False
        self._clsProperties = {}
        self._opProperties = {}
        self._owlTriplesUri = []

    def getClsProperties(self, clsUri: str) -> ClsProperties:
        if clsUri in self._clsProperties.keys():
            return self._clsProperties[clsUri]
        else:
            raise Exception("Unknown URI %s." % clsUri)

    def getFilepath(self) -> str:
        return self._filepath

    @abstractmethod
    def getName(self, uri: str) -> str:
        raise NotImplementedError("user must define getName")

    @abstractmethod
    def getNbErrors(self) -> int:
        raise NotImplementedError("user must define getNbErrors")

    def getOpNames(self) -> list:
        OPnames = [self.getName(key) for key in self._opProperties.keys()]
        return OPnames

    def getOpProperties(self, opUri: str) -> OpProperties:
        if opUri in self._opProperties.keys():
            return self._opProperties[opUri]
        else:
            raise Exception("Unknown URI %s." % opUri)

    def getOwlTriplesUri(self) -> list:
        return self._owlTriplesUri

    def isLoaded(self) -> bool:
        return self._loaded
