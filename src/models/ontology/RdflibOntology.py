from src.CST import CST
from src.models.ontology.AbstractOntology import AbstractOntology
from src.models.ontology.ClsData import ClsData
from src.models.ontology.OpData import OpData
from rdflib.exceptions import ParserError
from src.util import iri_to_name
from src.util import is_restriction_id

import rdflib as rl


def _is_class(_, p, o) -> bool:
    """
        Check if iri triple indicates a OWL class.
        Patterns:
        - s type class
        - s subClassOf o
        :param _: the iri to check.
        :param p: the current predicate.
        :param o: the current range.
        :return: True if _ represent a class.
    """
    return (p.toPython() == CST.IRI.RDF_TYPE and o.toPython() == CST.IRI.CLASS) or \
           (p.toPython() == CST.IRI.SUB_CLASS_OF)


def _is_object_property(_, p, o) -> bool:
    """
        Check if iri triple indicates an OWL object property.
        Patterns:
        - s type ObjectProperty
        :param _: the iri to check.
        :param p: the current predicate.
        :param o: the current range.
        :return: True if _ represent an OP.
    """
    return p.toPython() == CST.IRI.RDF_TYPE and o.toPython() == CST.IRI.OBJECT_PROPERTY


def _is_restriction(_, p, o) -> bool:
    """
        Check if iri triple indicates an OWL restriction.
        Patterns:
        - s type Restriction
        :param _: the iri to check.
        :param p: the current predicate.
        :param o: the current range.
        :return: True if _ represent an OWL restriction.
    """
    return p.toPython() == CST.IRI.RDF_TYPE and o.toPython() == CST.IRI.RESTRICTION


class RdflibOntology(AbstractOntology):
    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str, fileFormat: str = None):
        """
            Constructor of RdflibOntology.
            :param filepath: path to the ontology file.
            :param fileFormat: format used for reading the ontology with Rdflib.
        """
        super().__init__(filepath)
        self.__fileFormat = fileFormat
        self.__load()

    def getNbErrors(self) -> int:
        """
            Override
        """
        return 0

    # ---------------------------------------- PRIVATE ---------------------------------------- #
    def __load(self):
        """
            Private function for loading ontology.
            :param filepath: path to the ontology file.
        """
        if self.__fileFormat is None:
            formats_to_test = CST.RDFLIB_FORMATS
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
        """
            Private method for updating data from Rdflib ontology object.
            :param graph: the Rdflib object.
        """
        # Init class characteristics
        clssIris = [s.toPython() for s, p, o in graph if _is_class(s, p, o) and not is_restriction_id(s)]
        clssIris.append(CST.IRI.THING)
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
                if p == CST.IRI.DOMAIN:
                    opsData[s].domainsIris.append(o)
                    if o not in clssData.keys():
                        clsData = ClsData(iri=o)
                        clsData.name = iri_to_name(o)
                        clssData[o] = clsData
                    clssData[o].domainOfIris.append(s)
                elif p == CST.IRI.RANGE:
                    opsData[s].rangesIris.append(o)
                    if o not in clssData.keys():
                        clsData = ClsData(iri=o)
                        clsData.name = iri_to_name(o)
                        clssData[o] = clsData
                    clssData[o].rangeOfIris.append(s)
                elif p == CST.IRI.SUB_PROPERTY_OF:
                    opsData[s].subPropertyOfIris.append(o)
                    if o not in opsData.keys():
                        opData = OpData(self.getFilepath())
                        opData.iri = o
                        opData.name = iri_to_name(o)
                        opsData[o] = opData
                elif p == CST.IRI.INVERSE_OF:
                    opsData[s].inverseOfIri = o
                elif p == CST.IRI.LABEL:
                    opsData[s].label = o
                elif p == CST.IRI.RDF_TYPE:
                    if o == CST.IRI.MATH_PROPERTIES.ASYMMETRIC:
                        opsData[s].asymmetric = True
                    if o == CST.IRI.MATH_PROPERTIES.FUNCTIONAL:
                        opsData[s].functional = True
                    elif o == CST.IRI.MATH_PROPERTIES.INVERSE_FUNCTIONAL:
                        opsData[s].inverseFunctional = True
                    elif o == CST.IRI.MATH_PROPERTIES.IRREFLEXIVE:
                        opsData[s].irreflexive = True
                    elif o == CST.IRI.MATH_PROPERTIES.REFLEXIVE:
                        opsData[s].reflexive = True
                    elif o == CST.IRI.MATH_PROPERTIES.SYMMETRIC:
                        opsData[s].symmetric = True
                    elif o == CST.IRI.MATH_PROPERTIES.TRANSITIVE:
                        opsData[s].transitive = True
            elif p == CST.IRI.RDF_TYPE and o in clssIris:
                clssData[o].nbInstances += 1
            elif s in clssIris:
                if p == CST.IRI.SUB_CLASS_OF:
                    clssData[s].subClassOfIris.append(o)

        self._opsData = opsData
        self._clssData = clssData

        for opData in opsData.values():
            if len(opData.getDomainsIris()) == 0:
                opData.domainsIris.append(CST.IRI.THING)
            if len(opData.getRangesIris()) == 0:
                opData.rangesIris.append(CST.IRI.THING)

            for domainIRI in opData.getDomainsIris():
                domain = self.getClsData(domainIRI)
                opData.nbInstDomains.append(domain.nbInstances)
            for rangeIRI in opData.getRangesIris():
                range_ = self.getClsData(rangeIRI)
                opData.nbInstRanges.append(range_.nbInstances)
