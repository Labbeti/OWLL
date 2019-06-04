
from Config import *
from ontology.AbstractOntology import AbstractOntology
from ontology.ClsProperties import ClsProperties
from ontology.OpProperties import OpProperties
from rdflib.exceptions import ParserError

import rdflib as rdf


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
    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str, fileFormat: str = None):
        super().__init__(filepath)
        self.__fileFormat = fileFormat

        self.__load()

    def getName(self, uri: str) -> str:
        return _rl_uri_to_name(uri)

    def getNbErrors(self) -> int:
        return 0

    # ---------------------------------------- PRIVATE ---------------------------------------- #
    def __load(self):
        if self.__fileFormat is None:
            formats_to_test = Config.RDFLIB_FORMATS
        else:
            formats_to_test = [self.__fileFormat]

        graph = rdf.Graph()
        i = 0
        self._loaded = False
        while i < len(formats_to_test) and not self._loaded:
            format_name = formats_to_test[i]
            try:
                graph.load(self.getFilepath(), format=format_name)
                super()._loaded = True
            except (ParserError, ValueError, Exception):
                pass
            i += 1
        if self.isLoaded():
            self.__updateProperties(graph)
            self.__updateOWLTriples(graph)

    def __updateProperties(self, graph):
        # Init class characteristics
        clsUri = [s.toPython() for s, p, o in graph if _is_class(s, p, o)]
        clsChars = {s: ClsProperties() for s in clsUri}
        # Init OP characteristics
        opsUri = [s.toPython() for s, p, o in graph if _is_object_property(s, p, o)]
        opChars = {s: OpProperties() for s in opsUri}

        # Update OP characteristics
        for sUri, pUri, oUri in graph:
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
            elif s in clsUri:
                if p == Config.URI.SUB_CLASS_OF:
                    clsChars[s].subClassOf.append(o)

        self.__opChars = opChars
        self.__clsChars = clsChars

    def __updateOWLTriples(self, graph):
        # Update OWL triples
        self._owlTriplesUri = []
        opsUri = [s.toPython() for s, p, o in graph if _is_object_property(s, p, o)]

        for opUri in opsUri:
            domains = self._opProperties[opUri].domains
            if len(domains) == 0:
                domains = [Config.URI.THING]
            ranges = self._opProperties[opUri].ranges
            if len(ranges) == 0:
                ranges = [Config.URI.THING]

            for opDomain in domains:
                for opRange in ranges:
                    self._owlTriplesUri.append((opDomain, opUri, opRange))
