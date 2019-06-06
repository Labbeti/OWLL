
from Config import *
from ontology.AbstractOntology import AbstractOntology
from ontology.ClsProperties import ClsProperties
from ontology.OpProperties import OpProperties
from rdflib.exceptions import ParserError

import rdflib as rl
import re


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


# Patterns:
# - s type Restriction
def _is_restriction(_, p, o) -> bool:
    return p.toPython() == Config.URI.RDF_TYPE and o.toPython() == Config.URI.RESTRICTION


def _is_restriction_id(string: str) -> bool:
    return re.match("N[a-f0-9]+", string) is not None


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

        graph = rl.Graph()
        i = 0
        self._loaded = False
        while i < len(formats_to_test) and not self._loaded:
            format_name = formats_to_test[i]
            try:
                graph.load(self.getFilepath(), format=format_name)
                self._loaded = True
            except (ParserError, ValueError, Exception):
                pass
            i += 1
        if self.isLoaded():
            self.__updateProperties(graph)
            self.__updateOWLTriples(graph)

    def __updateProperties(self, graph):
        # Init class characteristics
        clsUri = [s.toPython() for s, p, o in graph if _is_class(s, p, o) and not _is_restriction_id(s)]
        clsProps = {s: ClsProperties() for s in clsUri}
        clsProps[Config.URI.THING] = ClsProperties()
        # Init OP characteristics
        opsUri = [s.toPython() for s, p, o in graph if _is_object_property(s, p, o)]
        opProps = {s: OpProperties() for s in opsUri}

        restrictionsClsId = set()

        # Update OP characteristics
        for sUri, pUri, oUri in graph:
            s = sUri.toPython()
            p = pUri.toPython()
            o = oUri.toPython()

            # if s is an op, check the predicate p
            if s in opsUri:
                if p == Config.URI.DOMAIN:
                    opProps[s].domains.append(o)
                    if o not in clsProps.keys():
                        clsProps[o] = ClsProperties()
                    clsProps[o].domainOf.append(s)
                elif p == Config.URI.RANGE:
                    opProps[s].ranges.append(o)
                    if o not in clsProps.keys():
                        clsProps[o] = ClsProperties()
                    clsProps[o].rangeOf.append(s)
                elif p == Config.URI.SUB_PROPERTY_OF:
                    opProps[s].subPropertyOf.append(o)
                elif p == Config.URI.INVERSE_OF:
                    opProps[s].inverseOf = o
                elif p == Config.URI.LABEL:
                    opProps[s].label = o
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
            elif p == Config.URI.RDF_TYPE and o in clsUri:
                clsProps[o].nbInstances += 1
            elif s in clsUri:
                if p == Config.URI.SUB_CLASS_OF:
                    clsProps[s].subClassOf.append(o)
                elif p == Config.URI.RDF_TYPE and o == Config.URI.RESTRICTION:
                    restrictionsClsId.add(s)

        self._opProperties = opProps
        self._clsProperties = clsProps

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
