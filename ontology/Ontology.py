from ontology.AbstractOntology import AbstractOntology
from ontology.LoadType import LoadType
from ontology.OPCharacteristics import OPCharacteristics
from ontology.OwlreadyOntology import OwlreadyOntology
from ontology.RdflibOntology import RdflibOntology


class Ontology(AbstractOntology):
    __onto: AbstractOntology = None

    # --- PUBLIC ---
    def __init__(self, filepath: str, load_type: LoadType = LoadType.TRY_BOTH, fileformat: str = None):
        self.__filepath = filepath
        self.__onto = None
        self.__load(filepath, load_type, fileformat)

    def getName(self, uri: str) -> str:
        if self.isLoaded():
            return self.__onto.getName(uri)
        else:
            raise Exception("Ontology %s not loaded." % self.__filepath)

    def getNbErrors(self) -> int:
        if self.isLoaded():
            return self.__onto.getNbErrors()
        else:
            return 1

    # Return the list of object properties names.
    def getObjectProperties(self) -> list:
        if self.isLoaded():
            return self.__onto.getObjectProperties()
        else:
            raise Exception("Ontology %s not loaded." % self.__filepath)

    def getOPCharacteristics(self, opUri: str) -> OPCharacteristics:
        if self.isLoaded():
            return self.__onto.getOPCharacteristics(opUri)
        else:
            raise Exception("Ontology %s not loaded." % self.__filepath)

    # Return the list of RDF triplets.
    def getOWLTriples(self) -> list:
        if self.isLoaded():
            return self.__onto.getOWLTriples()
        else:
            raise Exception("Ontology %s not loaded." % self.__filepath)

    def isLoaded(self) -> bool:
        return self.__onto is not None

    def isLoadedWithOR2(self) -> bool:
        return self.__onto is not None and isinstance(self.__onto, OwlreadyOntology)

    def isLoadedWithRL(self) -> bool:
        return self.__onto is not None and isinstance(self.__onto, RdflibOntology)

    # --- PRIVATE ---
    def __load(self, filepath, load_type, fileformat):
        if load_type == LoadType.TRY_BOTH:
            onto = RdflibOntology(filepath, fileformat)
            if onto.isLoaded():
                self.__onto = onto
            else:
                onto = OwlreadyOntology(filepath)
                if onto.isLoaded():
                    self.__onto = onto
        elif load_type == LoadType.FORCE_OWLREADY2:
            onto = OwlreadyOntology(filepath)
            if onto.isLoaded():
                self.__onto = onto
        elif load_type == LoadType.FORCE_RDFLIB:
            onto = RdflibOntology(filepath, fileformat)
            if onto.isLoaded():
                self.__onto = onto
        else:
            raise Exception("Invalid argument for \"load_type\".")
