from Csts import *
from ontology.AbstractOntology import AbstractOntology
from ontology.ClsProperties import ClsProperties
from ontology.OpProperties import OpProperties
from rdflib.exceptions import ParserError
from util import is_restriction_id

import rdflib as rl


# Patterns:
# - s type class
# - s subClassOf o
def _is_class(_, p, o) -> bool:
    return (p.toPython() == Csts.Uris.RDF_TYPE and o.toPython() == Csts.Uris.CLASS) or \
           (p.toPython() == Csts.Uris.SUB_CLASS_OF)


# Patterns:
# - s type ObjectProperty
def _is_object_property(_, p, o) -> bool:
    return p.toPython() == Csts.Uris.RDF_TYPE and o.toPython() == Csts.Uris.OBJECT_PROPERTY


# Patterns:
# - s type Restriction
def _is_restriction(_, p, o) -> bool:
    return p.toPython() == Csts.Uris.RDF_TYPE and o.toPython() == Csts.Uris.RESTRICTION


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
            formats_to_test = Csts.RDFLIB_FORMATS
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
        clsUri = [s.toPython() for s, p, o in graph if _is_class(s, p, o) and not is_restriction_id(s)]
        clsUri.append(Csts.Uris.THING)
        clsProps = {s: ClsProperties() for s in clsUri}
        # Init OP characteristics
        opsUri = [s.toPython() for s, p, o in graph if _is_object_property(s, p, o)]
        opProps = {s: OpProperties() for s in opsUri}

        # Update OP characteristics
        for sUri, pUri, oUri in graph:
            s = sUri.toPython()
            p = pUri.toPython()
            o = oUri.toPython()

            # if s is an op, check the predicate p
            if s in opsUri:
                if p == Csts.Uris.DOMAIN:
                    opProps[s].domains.append(o)
                    if o not in clsProps.keys():
                        clsProps[o] = ClsProperties()
                    clsProps[o].domainOf.append(s)
                elif p == Csts.Uris.RANGE:
                    opProps[s].ranges.append(o)
                    if o not in clsProps.keys():
                        clsProps[o] = ClsProperties()
                    clsProps[o].rangeOf.append(s)
                elif p == Csts.Uris.SUB_PROPERTY_OF:
                    opProps[s].subPropertyOf.append(o)
                elif p == Csts.Uris.INVERSE_OF:
                    opProps[s].inverseOf = o
                elif p == Csts.Uris.LABEL:
                    opProps[s].label = o
                elif p == Csts.Uris.RDF_TYPE:
                    if o == Csts.Uris.Properties.ASYMMETRIC:
                        opProps[s].isAsymmetric = True
                    if o == Csts.Uris.Properties.FUNCTIONAL:
                        opProps[s].isFunctional = True
                    elif o == Csts.Uris.Properties.INVERSE_FUNCTIONAL:
                        opProps[s].isInverseFunctional = True
                    elif o == Csts.Uris.Properties.IRREFLEXIVE:
                        opProps[s].isIrreflexive = True
                    elif o == Csts.Uris.Properties.REFLEXIVE:
                        opProps[s].isReflexive = True
                    elif o == Csts.Uris.Properties.SYMMETRIC:
                        opProps[s].isSymmetric = True
                    elif o == Csts.Uris.Properties.TRANSITIVE:
                        opProps[s].isTransitive = True
            elif p == Csts.Uris.RDF_TYPE and o in clsUri:
                clsProps[o].nbInstances += 1
            elif s in clsUri:
                if p == Csts.Uris.SUB_CLASS_OF:
                    clsProps[s].subClassOf.append(o)

        self._opProperties = opProps
        self._clsProperties = clsProps

    def __updateOWLTriples(self, graph):
        # Update OWL triples
        self._owlTriplesUri = []
        opsUri = [s.toPython() for s, p, o in graph if _is_object_property(s, p, o)]

        for opUri in opsUri:
            domains = self._opProperties[opUri].domains
            if len(domains) == 0:
                domains = [Csts.Uris.THING]
            ranges = self._opProperties[opUri].ranges
            if len(ranges) == 0:
                ranges = [Csts.Uris.THING]

            for opDomain in domains:
                for opRange in ranges:
                    self._owlTriplesUri.append((opDomain, opUri, opRange))
