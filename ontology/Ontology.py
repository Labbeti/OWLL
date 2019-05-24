
from ontology.AbstractOntology import AbstractOntology
from ontology.OwlreadyOntology import OwlreadyOntology
from ontology.RdflibOntology import RdflibOntology
from Config import *
from enum import Enum, unique


@unique
class LoadType(Enum):
    TRY_BOTH = 0
    FORCE_OWLREADY2 = 1
    FORCE_RDFLIB = 2


class Ontology(AbstractOntology):
    __onto: AbstractOntology = None

    def __init__(self, filepath: str, load_type: LoadType = LoadType.TRY_BOTH, fileformat: str = None):
        self.__filepath = filepath
        self.__onto = None
        self.__load(filepath, load_type, fileformat)

    def getNbErrors(self) -> int:
        return 0 if self.__onto is None else self.__onto.getNbErrors()

    # Return the list of object properties names.
    def getObjectProperties(self) -> list:
        if self.__onto is not None:
            return self.__onto.getObjectProperties()
        else:
            raise Exception("Ontology not loaded.")

    # Return the list of RDF triplets.
    def getOWLTriples(self) -> list:
        if self.__onto is not None:
            return self.__onto.getOWLTriples()
        else:
            raise Exception("Ontology not loaded.")

    def isLoaded(self) -> bool:
        return self.__onto is not None

    def isLoadedWithOR2(self) -> bool:
        return self.__onto is not None and isinstance(self.__onto, OwlreadyOntology)

    def isLoadedWithRL(self) -> bool:
        return self.__onto is not None and isinstance(self.__onto, RdflibOntology)

    def __load(self, filepath, load_type, fileformat):
        # TODO : clean here
        if load_type == LoadType.TRY_BOTH:
            onto = OwlreadyOntology(filepath)
            if onto.isLoaded():
                self.__onto = onto
                # prt("OK: Loading with owlready2 successfull.")
            else:
                # prt("KO: Load \"%s\" with Owlready2 has failed. Trying with rdflib... " % filepath)
                onto = RdflibOntology(filepath, fileformat)
                if onto.isLoaded():
                    self.__onto = onto
                    # prt("OK: Loading with rdflib successfull.")
                else:
                    pass  # prt("KO: Load \"%s\" failed with Rdflib too. Cannot read the file." % filepath)
        elif load_type == LoadType.FORCE_OWLREADY2:
            onto = OwlreadyOntology(filepath)
            if onto.isLoaded():
                self.__onto = onto
                # prt("OK: Loading with owlready2 successfull.")
            else:
                pass  # prt("KO: Load \"%s\" with Owlready2 has failed." % filepath)
        elif load_type == LoadType.FORCE_RDFLIB:
            onto = RdflibOntology(filepath, fileformat)
            if onto.isLoaded():
                self.__onto = onto
                # prt("OK: Loading with rdflib successfull.")
            else:
                pass  # prt("KO: Load \"%s\" with Rdflib has failed." % filepath)
        else:
            raise Exception("Invalid argument for \"load_type\".")