
from Config import *
from ontology.AbstractOntology import AbstractOntology
from ontology.ClassCharacteristics import ClassCharacteristics
from ontology.OPCharacteristics import OPCharacteristics
from rdflib.exceptions import ParserError

import rdflib as rl


def _is_class(_, p, o) -> bool:
    return (p.toPython() == Config.URI.RDF_TYPE and o.toPython() == Config.URI.CLASS) or \
           (p.toPython() == Config.URI.SUB_CLASS_OF)


# Patterns:
# - s type ObjectProperty
def _is_object_property(_, p, o) -> bool:
    return p.toPython() == Config.URI.RDF_TYPE and o.toPython() == Config.URI.OBJECT_PROPERTY


# Clean ontology name for each property
# (ex: http://semanticweb.org/tabletopgames_V3#contains -> contains)
def _get_name_rl(string: str) -> str:
    index = max(string.rfind("#"), string.rfind("/"))
    return string[index + 1:]


class RdflibOntology(AbstractOntology):
    def __init__(self, filepath: str, fileformat: str = None):
        self.__filepath = filepath
        self.__triples = []
        self.__arrows = {}

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

            claUri = [s.toPython() for s, p, o in self.__rl_graph if _is_class(s, p, o)]
            clProps = {s: ClassCharacteristics() for s in claUri}
            opsUri = [s.toPython() for s, p, o in self.__rl_graph if _is_object_property(s, p, o)]
            opProps = {s: OPCharacteristics() for s in opsUri}
            for sUri, pUri, oUri in self.__rl_graph:
                s = sUri.toPython()
                p = pUri.toPython()
                o = oUri.toPython()
                print("RDF triple = %s %s %s " % (sUri.toPython(), pUri.toPython(), oUri.toPython()))  # TODO clean
                if s in opsUri:
                    if p == Config.URI.DOMAIN:
                        opProps[s].domains.append(o)
                    elif p == Config.URI.RANGE:
                        opProps[s].ranges.append(o)
                    elif p == Config.URI.SUB_PROPERTY_OF:
                        opProps[s].subPropertyOf.append(o)
                    elif p == Config.URI.INVERSE_OF:
                        opProps[s].inverseOf = o
                    elif p == Config.URI.RDF_TYPE:
                        if o == Config.URI.CHARACTERISTIC.ASYMMETRIC:
                            opProps[s].isAsymmetric = True
                        if o == Config.URI.CHARACTERISTIC.FUNCTIONAL:
                            opProps[s].isFunctional = True
                        elif o == Config.URI.CHARACTERISTIC.INVERSE_FUNCTIONAL:
                            opProps[s].isInverseFunctional = True
                        elif o == Config.URI.CHARACTERISTIC.IRREFLEXIVE:
                            opProps[s].isIrreflexive = True
                        elif o == Config.URI.CHARACTERISTIC.REFLEXIVE:
                            opProps[s].isReflexive = True
                        elif o == Config.URI.CHARACTERISTIC.SYMMETRIC:
                            opProps[s].isSymmetric = True
                        elif o == Config.URI.CHARACTERISTIC.TRANSITIVE:
                            opProps[s].isTransitive = True
                elif p == Config.URI.RDF_TYPE and o in opsUri:
                    opProps[o].nbInstances += 1

            self.__opProps = opProps
            self.__clProps = clProps
            self.__triples = []
            for opUri in opsUri:
                domains = opProps[opUri].domains
                if len(domains) == 0:
                    domains = [Config.URI.THING]
                ranges = opProps[opUri].ranges
                if len(ranges) == 0:
                    ranges = [Config.URI.THING]

                for opDomain in domains:
                    for opRange in ranges:
                        self.__triples.append((opDomain, opUri, opRange))

    def getClassCharacteristics(self, clUri) -> ClassCharacteristics:
        return self.__clProps[clUri]

    def getName(self, uri: str) -> str:
        return _get_name_rl(uri)

    def getNbErrors(self) -> int:
        return 0

    # Warning: Not verified for all types of object properties.
    def getObjectProperties(self) -> list:
        return [_get_name_rl(s) for s, p, o in self.__rl_graph if _is_object_property(s, p, o)]

    def getOPCharacteristics(self, opUri: str) -> OPCharacteristics:
        return self.__opProps[opUri]

    def getOWLTriples(self) -> list:
        return self.__triples

    def isLoaded(self) -> bool:
        return self.__rl_graph is not None
