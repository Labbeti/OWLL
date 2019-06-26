from src.CST import *
from src.ontology.AbstractOntology import AbstractOntology
from src.ontology.ClsData import ClsData
from src.ontology.OpData import OpData
from urllib.error import HTTPError
from src.util import iri_to_name

import owlready2 as or2


class OwlreadyOntology(AbstractOntology):
    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self.__nb_errors = 0
        self.__load(filepath)

    def getNbErrors(self) -> int:
        return self.__nb_errors

    # ---------------------------------------- PRIVATE ---------------------------------------- #
    def __load(self, filepath: str):
        self.__nb_errors = 0
        ontoOwlready = None

        try:
            world = or2.World()
            ontoOwlready = world.get_ontology("file://" + filepath)
            ontoOwlready.loadFromFile(only_local=False)
            self._loaded = True
        except (or2.base.OwlReadyOntologyParsingError, HTTPError, ValueError, TypeError, UnboundLocalError,
                AttributeError):
            self._loaded = False

        if self.isLoaded():
            self.__updateData(ontoOwlready)

    def __updateData(self, ontoOwlready: or2.Ontology):
        for clsOwlready in ontoOwlready.classes():
            clsData = ClsData()
            clsData.subClassOfIris = clsOwlready.is_a
            clsData.iri = clsOwlready.iri
            clsData.name = iri_to_name(clsOwlready.iri)
            self._clssData[clsOwlready.iri] = clsData
        self._clssData[CST.IRI.THING] = ClsData()

        individuals = ontoOwlready.individuals()
        for individual in individuals:
            for cls in individual.is_a:
                try:
                    self._clssData[cls.iri].nbInstances += 1
                except AttributeError:
                    self.__nb_errors += 1

        for opOwlready in ontoOwlready.object_properties():
            opData = OpData(self.getFilepath())
            try:
                self.__inverseOf = opOwlready.inverse_property.iri if opOwlready.inverse_property is not None \
                    else []
            except AttributeError:
                self.__nb_errors += 1
            opData.asymmetric = issubclass(opOwlready, or2.AsymmetricProperty)
            opData.functional = issubclass(opOwlready, or2.FunctionalProperty)
            opData.inverseFunctional = issubclass(opOwlready, or2.InverseFunctionalProperty)
            opData.irreflexive = issubclass(opOwlready, or2.IrreflexiveProperty)
            opData.reflexive = issubclass(opOwlready, or2.ReflexiveProperty)
            opData.symmetric = issubclass(opOwlready, or2.SymmetricProperty)
            opData.transitive = issubclass(opOwlready, or2.TransitiveProperty)
            opData.label = opOwlready.label if opOwlready.label is not None else ""
            opData.subPropertyOf = [propOwlready.iri for propOwlready in opOwlready.is_a]
            opData.iri = opOwlready.iri
            opData.name = iri_to_name(opOwlready.iri)
            self._opsData[opOwlready.iri] = opData

            for domain_ in opOwlready.domain:
                if domain_ is not None:
                    try:
                        self._clssData[domain_.iri].domainOf.append(opOwlready.iri)
                    except AttributeError:
                        self.__nb_errors += 1
            for range_ in opOwlready.range:
                if range_ is not None:
                    try:
                        self._clssData[range_.iri].rangeOf.append(opOwlready.iri)
                    except AttributeError:
                        self.__nb_errors += 1

        for opData in self._opsData.values():
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
