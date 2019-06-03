
from Config import *
from ontology.AbstractOntology import AbstractOntology
from ontology.ClassCharacteristics import ClassCharacteristics
from ontology.OPCharacteristics import OPCharacteristics
from rdflib.exceptions import ParserError

import rdflib as rl


# Patterns:
# - s type class
# - s subClassOf o
def _is_class(_, p, o) -> bool:
    return (p.toPython() == Config.URI.RDF_TYPE and o.toPython() == Config.URI.CLASS) or \
           (p.toPython() == Config.URI.SUB_CLASS_OF)


# Patterns:
# - s type ObjectProperty
def _is_object_property(_, p, o) -> bool:
    return p.toPython() == Config.URI.RDF_TYPE and o.toPython() == Config.URI.OBJECT_PROPERTY


# Clean ontology name for each property
# (ex: http://semanticweb.org/tabletopgames_V3#contains -> contains)
def _rl_uri_to_name(string: str) -> str:
    if string == "":
        return ""
    if string[-1] == "/":
        string = string[:len(string)-1]
    index = max(string.rfind("#"), string.rfind("/"))
    return string[index + 1:]


class RdflibOntology(AbstractOntology):
    # --- PUBLIC ---
    def __init__(self, filepath: str, fileformat: str = None):
        self.__filepath = filepath
        self.__rl_graph = None
        self.__opCharacteristics = {}
        self.__clCharacteristics = {}
        self.__OWLtriples = []

        self.__load(filepath, fileformat)

    def getClassCharacteristics(self, clUri) -> ClassCharacteristics:
        return self.__clCharacteristics[clUri]

    def getName(self, uri: str) -> str:
        return _rl_uri_to_name(uri)

    def getNbErrors(self) -> int:
        return 0

    # Warning: Not verified for all types of object properties.
    def getObjectProperties(self) -> list:
        return [_rl_uri_to_name(s) for s, p, o in self.__rl_graph if _is_object_property(s, p, o)]

    def getOPCharacteristics(self, opUri: str) -> OPCharacteristics:
        return self.__opCharacteristics[opUri]

    def getOWLTriples(self) -> list:
        return self.__OWLtriples

    def isLoaded(self) -> bool:
        return self.__rl_graph is not None

    # --- PRIVATE ---
    def __load(self, filepath: str, fileformat: str):
        self.__filepath = filepath

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
            self.__updateProperties()
            self.__updateOWLTriples()

    def __updateProperties(self):
        # Init class characteristics
        claUri = [s.toPython() for s, p, o in self.__rl_graph if _is_class(s, p, o)]
        clChars = {s: ClassCharacteristics() for s in claUri}
        # Init OP characteristics
        opsUri = [s.toPython() for s, p, o in self.__rl_graph if _is_object_property(s, p, o)]
        opChars = {s: OPCharacteristics() for s in opsUri}

        # Update OP characteristics
        for sUri, pUri, oUri in self.__rl_graph:
            s = sUri.toPython()
            p = pUri.toPython()
            o = oUri.toPython()
            # if s is an op, check the predicate p
            if s in opsUri:
                if p == Config.URI.DOMAIN:
                    opChars[s].domains.append(o)
                elif p == Config.URI.RANGE:
                    opChars[s].ranges.append(o)
                elif p == Config.URI.SUB_PROPERTY_OF:
                    opChars[s].subPropertyOf.append(o)
                elif p == Config.URI.INVERSE_OF:
                    opChars[s].inverseOf = o
                elif p == Config.URI.LABEL:
                    opChars[s].label = o
                elif p == Config.URI.RDF_TYPE:
                    if o == Config.URI.CHARACTERISTIC.ASYMMETRIC:
                        opChars[s].isAsymmetric = True
                    if o == Config.URI.CHARACTERISTIC.FUNCTIONAL:
                        opChars[s].isFunctional = True
                    elif o == Config.URI.CHARACTERISTIC.INVERSE_FUNCTIONAL:
                        opChars[s].isInverseFunctional = True
                    elif o == Config.URI.CHARACTERISTIC.IRREFLEXIVE:
                        opChars[s].isIrreflexive = True
                    elif o == Config.URI.CHARACTERISTIC.REFLEXIVE:
                        opChars[s].isReflexive = True
                    elif o == Config.URI.CHARACTERISTIC.SYMMETRIC:
                        opChars[s].isSymmetric = True
                    elif o == Config.URI.CHARACTERISTIC.TRANSITIVE:
                        opChars[s].isTransitive = True
            elif p == Config.URI.RDF_TYPE and o in opsUri:
                opChars[o].nbInstances += 1

        self.__opCharacteristics = opChars
        self.__clCharacteristics = clChars

    def __updateOWLTriples(self):
        # Update OWL triples
        self.__OWLtriples = []
        opsUri = [s.toPython() for s, p, o in self.__rl_graph if _is_object_property(s, p, o)]

        for opUri in opsUri:
            domains = self.__opCharacteristics[opUri].domains
            if len(domains) == 0:
                domains = [Config.URI.THING]
            ranges = self.__opCharacteristics[opUri].ranges
            if len(ranges) == 0:
                ranges = [Config.URI.THING]

            for opDomain in domains:
                for opRange in ranges:
                    self.__OWLtriples.append((opDomain, opUri, opRange))
