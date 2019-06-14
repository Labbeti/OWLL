from ontology.AbstractOntology import AbstractOntology
from ontology.ClsData import ClsData
from ontology.IOntology import IOntology
from ontology.OpData import OpData
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

    def getAllOpsData(self) -> dict:
        self.__checkIfLoaded()
        return self.__onto.getAllOpsData()

    def getClsData(self, clsIri: str) -> ClsData:
        self.__checkIfLoaded()
        return self.__onto.getClsData(clsIri)

    def getFilepath(self) -> str:
        self.__checkIfLoaded()
        return self.__onto.getFilepath()

    def getName(self, iri: str) -> str:
        self.__checkIfLoaded()
        return self.__onto.getName(iri)

    def getNbErrors(self) -> int:
        if self.isLoaded():
            return self.__onto.getNbErrors()
        else:
            return 1

    def getOpNames(self) -> list:
        self.__checkIfLoaded()
        return self.__onto.getOpNames()

    def getOpData(self, opUri: str) -> OpData:
        self.__checkIfLoaded()
        return self.__onto.getOpData(opUri)

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
