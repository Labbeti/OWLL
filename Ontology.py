
from enum import Enum, unique
from rdflib.exceptions import ParserError
from urllib.error import HTTPError

import owlready2 as owl
import rdflib as rdf


# Clean ontology name for each property
# (ex: tabletopgames_V3.contains -> contains)
def _get_name_owlready2(string: str) -> str:
    index = string.rfind(".")
    return string[index+1:]


# Clean ontology name for each property
# (ex: http://semanticweb.org/tabletopgames_V3#contains -> contains)
def _get_name_rdflib(string: str) -> str:
    index = max(string.rfind("#"), string.rfind("/"))
    return string[index+1:]


@unique
class LoadType(Enum):
    TRY_BOTH = 0
    FORCE_OWLREADY2 = 1
    FORCE_RDFLIB = 2


class Ontology:
    __filepath: str = ""
    __owl_onto: owl.Ontology = None
    __rdf_graph: rdf.Graph = None
    __nb_errors: int = 0

    def __init__(self, filepath: str, load_type: LoadType = LoadType.TRY_BOTH):
        self.__filepath = filepath
        self.__errors = 0

        if load_type == LoadType.TRY_BOTH:
            try:
                self.__owlready2_load()
                print("§ Loading with owlready2 successfull.")
            except (owl.base.OwlReadyOntologyParsingError, HTTPError, TypeError):
                self.__owl_onto = None
                print("§ Load \"%s\" with Owlready2 has failed. Trying with rdflib... " % filepath)
                try:
                    self.__rdflib_load()
                    print("§ Loading with rdflib successfull.")
                except ParserError:
                    self.__rdf_graph = None
                    print("§ Load \"%s\" failed with Rdflib too. Cannot read the file." % filepath)
        elif load_type == LoadType.FORCE_OWLREADY2:
            try:
                self.__owlready2_load()
                print("§ Loading with owlready2 successfull.")
            except (owl.base.OwlReadyOntologyParsingError, HTTPError, TypeError):
                self.__owl_onto = None
                print("§ Load \"%s\" with Owlready2 has failed." % filepath)
        elif load_type == LoadType.FORCE_RDFLIB:
            try:
                self.__rdflib_load()
                print("§ Loading with rdflib successfull.")
            except ParserError:
                self.__rdf_graph = None
                print("§ Load \"%s\" with Rdflib has failed." % filepath)
        else:
            raise Exception("Invalid argument \"load_type\".")

    # Return the list of object properties names.
    def get_obj_prop_names(self) -> list:
        if self.is_loaded_with_owlready2():
            return self.__owlready2_get_obj_prop_names()
        elif self.is_loaded_with_rdflib():
            return self.__rdflib_get_obj_prop_names()
        else:
            raise Exception("Ontology not loaded.")

    # Return the list of RDF triplets.
    def get_owl_triples(self):
        if self.is_loaded_with_owlready2():
            return self.__owlready2_get_owl_triples()
        elif self.is_loaded_with_rdflib():
            return self.__rdflib_get_owl_triples()
        else:
            raise Exception("Ontology not loaded.")

    def is_loaded_with_owlready2(self) -> bool:
        return self.__owl_onto is not None

    def is_loaded_with_rdflib(self) -> bool:
        return self.__rdf_graph is not None

    def is_loaded(self) -> bool:
        return self.is_loaded_with_owlready2() or self.is_loaded_with_rdflib()

    def get_nb_errors(self) -> int:
        return self.__nb_errors

    def __owlready2_load(self):
        self.__owl_onto = owl.get_ontology(self.__filepath)
        self.__owl_onto.load()

    def __rdflib_load(self):
        self.__rdf_graph = rdf.Graph()
        self.__rdf_graph.load(self.__filepath)

    # Warning: Does not work with some OWL format like Turtle
    def __owlready2_get_obj_prop_names(self) -> list:
        objprops = list(self.__owl_onto.object_properties())

        obj_prop_names = [_get_name_owlready2(objprop.name) for objprop in objprops]
        return obj_prop_names

    # Warning: Not verified for all types of object properties.
    def __rdflib_get_obj_prop_names(self) -> list:
        names = []
        for s, p, o in self.__rdf_graph:
            # Patterns:
            # - s type ObjectProperty
            # TODO : search for anothers patterns ?
            # - s type http://www.w3.org/2002/07/owl#FunctionalProperty
            # ? apparemment non car owlready2 ne considère pas pour dbpedia
            if p.toPython() == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" \
                    and o.toPython() == "http://www.w3.org/2002/07/owl#ObjectProperty":

                name = _get_name_rdflib(s.toPython())
                if name not in names:
                    names.append(name)
        return names

    def __owlready2_get_owl_triples(self) -> list:
        self.__nb_errors = 0
        triples = []
        for objprop in self.__owl_onto.object_properties():
            try:
                for op_domain in objprop.domain:
                    for op_range in objprop.range:
                        domain_name = _get_name_owlready2(op_domain.name)
                        objprop_name = _get_name_owlready2(objprop.name)
                        range_name = _get_name_owlready2(op_range.name)
                        triples.append((domain_name, objprop_name, range_name))
            except (TypeError, AttributeError):
                self.__nb_errors += 1
        return triples

    def __rdflib_get_owl_triples(self) -> list:
        object_properties = set(self.__rdflib_get_obj_prop_names())

        triples = [
            (_get_name_rdflib(s), _get_name_rdflib(p), _get_name_rdflib(o))
            for s, p, o in self.__rdf_graph
            if p in object_properties
        ]
        return triples
