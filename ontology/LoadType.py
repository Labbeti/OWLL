from enum import Enum, unique


# Enumerate for Ontology class.
@unique
class LoadType(Enum):
    TRY_BOTH = 0
    FORCE_OWLREADY2 = 1
    FORCE_RDFLIB = 2
