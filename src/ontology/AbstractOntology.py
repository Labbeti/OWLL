from abc import abstractmethod
from src.ontology.ClsData import ClsData
from src.ontology.IOntology import IOntology
from src.ontology.OpData import OpData

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


class AbstractOntology(IOntology):
    """
        Abstract Ontology for implementation with librairies.
    """

    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str):
        self._filepath = filepath
        self._loaded = False
        self._clssData = {}
        self._opsData = {}

    def getAllClsProperties(self) -> dict:
        return self._clssData

    def getAllOpsData(self) -> dict:
        return self._opsData

    def getClsData(self, clsIri: str) -> ClsData:
        if clsIri in self._clssData.keys():
            return self._clssData[clsIri]
        else:
            raise Exception("Unknown URI %s." % clsIri)

    def getFilepath(self) -> str:
        return self._filepath

    def getOpName(self, iri: str) -> str:
        if self.isLoaded() and iri in self._opsData.keys():
            return self._opsData[iri].name
        else:
            raise Exception("Invalid ontology or IRI for getName()")

    @abstractmethod
    def getNbErrors(self) -> int:
        raise NotImplementedError("user must define getNbErrors")

    def getOpNames(self) -> list:
        opNames = [opData.getOpName() for opData in self._opsData.values()]
        return opNames

    def getOpData(self, opUri: str) -> OpData:
        if opUri in self._opsData.keys():
            return self._opsData[opUri]
        else:
            raise Exception("Unknown URI %s." % opUri)

    def isLoaded(self) -> bool:
        return self._loaded
