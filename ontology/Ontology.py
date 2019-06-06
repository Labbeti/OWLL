from ontology.AbstractOntology import AbstractOntology
from ontology.ClsProperties import ClsProperties
from ontology.IOntology import IOntology
from ontology.OpProperties import OpProperties
from ontology.OwlreadyOntology import OwlreadyOntology
from ontology.RdflibOntology import RdflibOntology


# Strategy Pattern for managing ontologies with multiple librairies.
class Ontology(IOntology):
    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str, fileFormat: str = None):
        self.__onto: AbstractOntology
        self.__load(filepath, fileFormat)

    def getAllClsProperties(self) -> dict:
        self.__checkIfLoaded()
        return self.__onto.getAllClsProperties()

    def getClsProperties(self, clsUri: str) -> ClsProperties:
        self.__checkIfLoaded()
        return self.__onto.getClsProperties(clsUri)

    def getFilepath(self) -> str:
        self.__checkIfLoaded()
        return self.__onto.getFilepath()

    def getName(self, uri: str) -> str:
        self.__checkIfLoaded()
        return self.__onto.getName(uri)

    def getNbErrors(self) -> int:
        if self.isLoaded():
            return self.__onto.getNbErrors()
        else:
            return 1

    def getOpNames(self) -> list:
        self.__checkIfLoaded()
        return self.__onto.getOpNames()

    def getOpProperties(self, opUri: str) -> OpProperties:
        self.__checkIfLoaded()
        return self.__onto.getOpProperties(opUri)

    def getOwlTriplesUri(self) -> list:
        self.__checkIfLoaded()
        return self.__onto.getOwlTriplesUri()

    def isLoaded(self) -> bool:
        return self.__onto is not None and self.__onto.isLoaded()

    def isLoadedWithOR2(self) -> bool:
        return self.isLoaded() and isinstance(self.__onto, OwlreadyOntology)

    def isLoadedWithRL(self) -> bool:
        return self.isLoaded() and isinstance(self.__onto, RdflibOntology)

    # ---------------------------------------- PRIVATE ---------------------------------------- #
    def __load(self, filepath, fileformat):
        self.__onto = None
        onto = RdflibOntology(filepath, fileformat)
        if onto.isLoaded():
            self.__onto = onto
        else:
            onto = OwlreadyOntology(filepath)
            if onto.isLoaded():
                self.__onto = onto

    def __checkIfLoaded(self):
        if not self.isLoaded():
            raise Exception("Ontology %s not loaded." % self.__onto.getFilepath())
