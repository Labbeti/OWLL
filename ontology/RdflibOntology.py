from Csts import *
from ontology.AbstractOntology import AbstractOntology
from ontology.ClsData import ClsData
from ontology.OpData import OpData
from rdflib.exceptions import ParserError
from util import iri_to_name
from util import is_restriction_id

import rdflib as rl


# Patterns:
# - s type class
# - s subClassOf o
def _is_class(_, p, o) -> bool:
    return (p.toPython() == Csts.IRIs.RDF_TYPE and o.toPython() == Csts.IRIs.CLASS) or \
           (p.toPython() == Csts.IRIs.SUB_CLASS_OF)


# Patterns:
# - s type ObjectProperty
def _is_object_property(_, p, o) -> bool:
    return p.toPython() == Csts.IRIs.RDF_TYPE and o.toPython() == Csts.IRIs.OBJECT_PROPERTY


# Patterns:
# - s type Restriction
def _is_restriction(_, p, o) -> bool:
    return p.toPython() == Csts.IRIs.RDF_TYPE and o.toPython() == Csts.IRIs.RESTRICTION


class RdflibOntology(AbstractOntology):
    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str, fileFormat: str = None):
        super().__init__(filepath)
        self.__fileFormat = fileFormat
        self.__load()

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
            self.__updateData(graph)

    def __updateData(self, graph):
        # Init class characteristics
        clssIris = [s.toPython() for s, p, o in graph if _is_class(s, p, o) and not is_restriction_id(s)]
        clssIris.append(Csts.IRIs.THING)
        clssData = {s: ClsData() for s in clssIris}
        for clsIri, clsData in clssData.items():
            clsData.iri = clsIri
            clsData.name = iri_to_name(clsIri)

        # Init OP characteristics
        opsIris = [s.toPython() for s, p, o in graph if _is_object_property(s, p, o)]
        opsData = {s: OpData(self.getFilepath()) for s in opsIris}
        for opIri, opData in opsData.items():
            opData.iri = opIri
            opData.name = iri_to_name(opIri)

        # Update OP characteristics
        for sUri, pUri, oUri in graph:
            s = sUri.toPython()
            p = pUri.toPython()
            o = oUri.toPython()
            # print("DEBUG: triples: ", s, p, o)

            # if s is an op, check the predicate p
            if s in opsIris:
                if p == Csts.IRIs.DOMAIN:
                    opsData[s].domainsIris.append(o)
                    if o not in clssData.keys():
                        clsData = ClsData(iri=o)
                        clsData.name = iri_to_name(o)
                        clssData[o] = clsData
                    clssData[o].domainOfIris.append(s)
                elif p == Csts.IRIs.RANGE:
                    opsData[s].rangesIris.append(o)
                    if o not in clssData.keys():
                        clsData = ClsData(iri=o)
                        clsData.name = iri_to_name(o)
                        clssData[o] = clsData
                    clssData[o].rangeOfIris.append(s)
                elif p == Csts.IRIs.SUB_PROPERTY_OF:
                    opsData[s].subPropertyOfIris.append(o)
                    if o not in opsData.keys():
                        opData = OpData(self.getFilepath())
                        opData.iri = o
                        opData.name = iri_to_name(o)
                        opsData[o] = opData
                elif p == Csts.IRIs.INVERSE_OF:
                    opsData[s].inverseOfIri = o
                elif p == Csts.IRIs.LABEL:
                    opsData[s].label = o
                elif p == Csts.IRIs.RDF_TYPE:
                    if o == Csts.IRIs.Properties.ASYMMETRIC:
                        opsData[s].asymmetric = True
                    if o == Csts.IRIs.Properties.FUNCTIONAL:
                        opsData[s].functional = True
                    elif o == Csts.IRIs.Properties.INVERSE_FUNCTIONAL:
                        opsData[s].inverseFunctional = True
                    elif o == Csts.IRIs.Properties.IRREFLEXIVE:
                        opsData[s].irreflexive = True
                    elif o == Csts.IRIs.Properties.REFLEXIVE:
                        opsData[s].reflexive = True
                    elif o == Csts.IRIs.Properties.SYMMETRIC:
                        opsData[s].symmetric = True
                    elif o == Csts.IRIs.Properties.TRANSITIVE:
                        opsData[s].transitive = True
            elif p == Csts.IRIs.RDF_TYPE and o in clssIris:
                clssData[o].nbInstances += 1
            elif s in clssIris:
                if p == Csts.IRIs.SUB_CLASS_OF:
                    clssData[s].subClassOfIris.append(o)

        self._opsData = opsData
        self._clssData = clssData

        for opData in opsData.values():
            if len(opData.getDomainsIris()) == 0:
                opData.domainsIris.append(Csts.IRIs.THING)
            if len(opData.getRangesIris()) == 0:
                opData.rangesIris.append(Csts.IRIs.THING)

            for domainIRI in opData.getDomainsIris():
                domain = self.getClsData(domainIRI)
                opData.nbInstDomains.append(domain.nbInstances)
            for rangeIRI in opData.getRangesIris():
                range_ = self.getClsData(rangeIRI)
                opData.nbInstRanges.append(range_.nbInstances)
