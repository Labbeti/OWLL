
from Config import *
from onto_classes.AbstractOntology import AbstractOntology
from rdflib.exceptions import ParserError

import rdflib as rl


# Patterns:
# - s type ObjectProperty
# TODO : search for anothers patterns ?
# - s type http://www.w3.org/2002/07/owl#FunctionalProperty
# ? apparemment non car owlready2 ne considère pas pour dbpedia
def _is_object_property(s, p, o) -> bool:
    return p.toPython() == Config.LINK_RDF_TYPE and o.toPython() == Config.LINK_OBJECT_PROPERTY


# Clean ontology name for each property
# (ex: http://semanticweb.org/tabletopgames_V3#contains -> contains)
def _get_name_rdflib(string: str) -> str:
    index = max(string.rfind("#"), string.rfind("/"))
    return string[index + 1:]


class RdflibOntology(AbstractOntology):
    __rl_graph: rl.Graph = None

    def __init__(self, filepath: str, fileformat: str):
        self.__filepath = filepath
        self.__rl_graph = None

        if fileformat is None:
            formats_to_test = Config.RDFLIB_FORMATS
        else:
            formats_to_test = [fileformat]

        graph = rl.Graph()
        i = 0
        loaded = False
        while i < len(formats_to_test) and not loaded:
            format_name = formats_to_test[i]
            try:
                graph.load(self.__filepath, format=format_name)
                loaded = True
            except (ParserError, ValueError, Exception):
                pass
            i += 1

        if loaded:
            self.__rl_graph = graph

    def getNbErrors(self) -> int:
        return 0

    # Warning: Not verified for all types of object properties.
    def getObjectProperties(self) -> list:
        return [_get_name_rdflib(s) for s, p, o in self.__rl_graph if _is_object_property(s, p, o)]

    def getOWLTriples(self) -> list:
        domains = {}
        ranges = {}
        ops = self.getObjectProperties()
        for sUri, pUri, oUri in self.__rl_graph:
            s = _get_name_rdflib(sUri.toPython())
            if s in ops:
                if pUri.toPython() == Config.LINK_DOMAIN:
                    domains[s] = oUri
                elif pUri.toPython() == Config.LINK_RANGE:
                    ranges[s] = oUri
        triples = []
        for op in ops:
            if op in domains.keys():
                domain = _get_name_rdflib(domains[op])
            else:
                domain = _get_name_rdflib(Config.LINK_THING)
            if op in ranges.keys():
                range = _get_name_rdflib(ranges[op])
            else:
                range = _get_name_rdflib(Config.LINK_THING)
            triples.append((domain, op, range))

        return triples

    def isLoaded(self) -> bool:
        return self.__rl_graph is not None
