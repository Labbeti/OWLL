
from abc import ABCMeta
from abc import abstractmethod
from ontology.OpProperties import OpProperties


'''
                        IOntology
                            ^
                            |
            +---------------+---------------+
            |                               |
            |                               |
        Ontology                      AbstractOntology
                                            ^
                                            |
                                +-----------+-----------+
                                |                       |
                                |                       |
                        OwlreadyOntology            RdflibOntology

'''


# Interface for Ontology classes.
class IOntology(object, metaclass=ABCMeta):
    # Return all class properties.
    @abstractmethod
    def getAllClsProperties(self) -> dict:
        raise NotImplementedError("user must define getAllClsProperties")

    # Return the properties of a class.
    @abstractmethod
    def getClsProperties(self, clsUri: str) -> str:
        raise NotImplementedError("user must define getClsProperties")

    # Get the filepath of the ontology file loaded.
    @abstractmethod
    def getFilepath(self) -> str:
        raise NotImplementedError("user must define getFilepath")

    # Return the name of the OP or class target by the parameter uri.
    @abstractmethod
    def getName(self, uri: str) -> str:
        raise NotImplementedError("user must define getName")

    # Return the number of errors encountered during loading of the ontology.
    @abstractmethod
    def getNbErrors(self) -> int:
        raise NotImplementedError("user must define getNbErrors")

    @abstractmethod
    # Return the list of object properties names.
    def getOpNames(self) -> list:
        raise NotImplementedError("user must define getOpNames")

    # Return the properties of an OP.
    @abstractmethod
    def getOpProperties(self, opUri: str) -> OpProperties:
        raise NotImplementedError("user must define getOpProperties")

    # Return the list of RDF triplets.
    @abstractmethod
    def getOwlTriplesUri(self) -> list:
        raise NotImplementedError("user must define getOwlTriplesUri")

    # Return True if is loading is succesfull.
    @abstractmethod
    def isLoaded(self) -> bool:
        raise NotImplementedError("user must define isLoaded")
