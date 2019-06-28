from abc import abstractmethod
from src.models.ontology.ClsData import ClsData
from src.models.ontology.IOntology import IOntology
from src.models.ontology.OpData import OpData

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
        Abstract Ontology class for implementation with differents librairies.
    """

    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str):
        """
            Constructor of AbstractOntology.
            :param filepath: path to the OWL file.
        """
        self._filepath = filepath
        self._loaded = False
        self._clssData = {}
        self._opsData = {}

    def getAllClsData(self) -> dict:
        """
            Override
        """
        return self._clssData

    def getAllOpsData(self) -> dict:
        """
            Override
        """
        return self._opsData

    def getClsData(self, clsIri: str) -> ClsData:
        """
            Override
        """
        if clsIri in self._clssData.keys():
            return self._clssData[clsIri]
        else:
            raise Exception("Unknown URI %s." % clsIri)

    def getFilepath(self) -> str:
        """
            Override
        """
        return self._filepath

    def getOpName(self, iri: str) -> str:
        """
            Override
        """
        if self.isLoaded() and iri in self._opsData.keys():
            return self._opsData[iri].name
        else:
            raise Exception("Invalid ontology or IRI for getName()")

    @abstractmethod
    def getNbErrors(self) -> int:
        """
            Override
        """
        raise NotImplementedError("user must define getNbErrors")

    def getOpNames(self) -> list:
        """
            Override
        """
        opNames = [opData.getOpName() for opData in self._opsData.values()]
        return opNames

    def getOpData(self, opUri: str) -> OpData:
        """
            Override
        """
        if opUri in self._opsData.keys():
            return self._opsData[opUri]
        else:
            raise Exception("Unknown URI %s." % opUri)

    def isLoaded(self) -> bool:
        """
            Override
        """
        return self._loaded
