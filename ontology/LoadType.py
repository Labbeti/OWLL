from enum import Enum, unique


@unique
class LoadType(Enum):
    TRY_BOTH = 0
    FORCE_OWLREADY2 = 1
    FORCE_RDFLIB = 2
