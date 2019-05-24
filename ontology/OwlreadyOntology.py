from Config import *
from ontology.AbstractOntology import AbstractOntology
from urllib.error import HTTPError
from utils import rem_duplicates

import owlready2 as or2


# Clean ontology name for each property
# (ex: tabletopgames_V3.contains -> contains)
def _get_name_or2(string: str) -> str:
    index = max(string.rfind("."), string.rfind("#"))
    return string[index + 1:]


class OwlreadyOntology(AbstractOntology):
    __nb_errors: int = 0
    __or2_onto: or2.Ontology = None
    __world = None

    def __init__(self, filepath: str):
        self.__filepath = filepath
        self.__nb_errors = 0

        try:
            self.__world = or2.World()
            or2_onto = self.__world.get_ontology("file://" + filepath)
            or2_onto.load(only_local=False)
            self.__or2_onto = or2_onto
        except (or2.base.OwlReadyOntologyParsingError, HTTPError, ValueError, TypeError, UnboundLocalError,
                AttributeError):
            self.__or2_onto = None

    def getNbErrors(self) -> int:
        return self.__nb_errors

    # Warning: Does not work with some OWL format like Turtle
    def getObjectProperties(self) -> list:
        objprops = list(self.__or2_onto.object_properties())
        obj_prop_names = [_get_name_or2(objprop.name) for objprop in objprops]
        return rem_duplicates(obj_prop_names)

    def getOWLTriples(self) -> list:
        self.__nb_errors = 0
        # Remove duplicates because Owlready2 contains errors (ex: for Restrictions on collaborativePizza.owl)
        ops = rem_duplicates(self.__or2_onto.object_properties())
        triples = []
        for op in ops:
            try:
                domains = [op_domain.name for op_domain in op.domain] if op.domain != [] else [Config.LINK_THING]
                ranges = [op_range.name for op_range in op.range] if op.range != [] else [Config.LINK_THING]
                for op_domain in domains:
                    for op_range in ranges:
                        domain_name = _get_name_or2(op_domain)
                        objprop_name = _get_name_or2(op.name)
                        range_name = _get_name_or2(op_range)
                        triples.append((domain_name, objprop_name, range_name))
            except (TypeError, AttributeError):
                self.__nb_errors += 1
        return triples

    def isLoaded(self) -> bool:
        return self.__or2_onto is not None
