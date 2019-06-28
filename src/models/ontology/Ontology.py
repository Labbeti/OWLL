from src.models.ontology.AbstractOntology import AbstractOntology
from src.models.ontology.ClsData import ClsData
from src.models.ontology.IOntology import IOntology
from src.models.ontology.OpData import OpData
from src.models.ontology.OwlreadyOntology import OwlreadyOntology
from src.models.ontology.RdflibOntology import RdflibOntology


class Ontology(IOntology):
    """
        Strategy Pattern for managing ontologies with multiple librairies.
    """

    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str, fileFormat: str = None):
        """
            Constructor of Ontology
            :param filepath: path to the ontology file.
            :param fileFormat: format used for parser the file.
        """
        self.__onto: AbstractOntology
        self.__load(filepath, fileFormat)

    def getAllClsData(self) -> dict:
        """
            Override
        """
        self.__checkIfLoaded()
        return self.__onto.getAllClsData()

    def getAllOpsData(self) -> dict:
        """
            Override
        """
        self.__checkIfLoaded()
        return self.__onto.getAllOpsData()

    def getClsData(self, clsIri: str) -> ClsData:
        """
            Override
        """
        self.__checkIfLoaded()
        return self.__onto.getClsData(clsIri)

    def getFilepath(self) -> str:
        """
            Override
        """
        self.__checkIfLoaded()
        return self.__onto.getFilepath()

    def getOpName(self, iri: str) -> str:
        """
            Override
        """
        self.__checkIfLoaded()
        return self.__onto.getOpName(iri)

    def getNbErrors(self) -> int:
        """
            Override
        """
        if self.isLoaded():
            return self.__onto.getNbErrors()
        else:
            return 1

    def getOpNames(self) -> list:
        """
            Override
        """
        self.__checkIfLoaded()
        return self.__onto.getOpNames()

    def getOpData(self, opUri: str) -> OpData:
        """
            Override
        """
        self.__checkIfLoaded()
        return self.__onto.getOpData(opUri)

    def isLoaded(self) -> bool:
        """
            Override
        """
        return self.__onto is not None and self.__onto.isLoaded()

    def isLoadedWithOR2(self) -> bool:
        """
            Override
        """
        return self.isLoaded() and isinstance(self.__onto, OwlreadyOntology)

    def isLoadedWithRL(self) -> bool:
        """
            Override
        """
        return self.isLoaded() and isinstance(self.__onto, RdflibOntology)

    # ---------------------------------------- PRIVATE ---------------------------------------- #
    def __load(self, filepath: str, fileformat: str):
        """
            Private method for loading a ontology.
            :param filepath: the path to ontology file.
            :param fileformat: the format used for loading with Rdflib.
        """
        self.__onto = None
        onto = RdflibOntology(filepath, fileformat)
        if onto.isLoaded():
            self.__onto = onto
        else:
            onto = OwlreadyOntology(filepath)
            if onto.isLoaded():
                self.__onto = onto

    def __checkIfLoaded(self):
        """
            Private method for raise exception if the ontology is not loaded.
        """
        if not self.isLoaded():
            raise Exception(
                "Ontology %s not loaded." % (self.__onto.getFilepath() if self.__onto is not None else "None")
            )
