from Csts import *
from ontology.AbstractOntology import AbstractOntology
from ontology.ClsProperties import ClsProperties
from ontology.OpProperties import OpProperties
from urllib.error import HTTPError
from util import prt
from util import rem_duplicates

import owlready2 as or2


# Clean ontology name for each property
# (ex: tabletopgames_V3.contains -> contains)
# (ex: org/ontology/isPartOfWineRegion -> isPartOfWineRegion)
def _or2_uri_to_name(string: str) -> str:
    index = max(string.rfind("."), string.rfind("#"), string.rfind("/"))
    return string[index + 1:]


class OwlreadyOntology(AbstractOntology):
    # ---------------------------------------- PUBLIC ---------------------------------------- #
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self.__nb_errors = 0

        self.__load(filepath)

    def getName(self, uri: str) -> str:
        return _or2_uri_to_name(uri)

    def getNbErrors(self) -> int:
        return self.__nb_errors

    # ---------------------------------------- PRIVATE ---------------------------------------- #
    def __load(self, filepath: str):
        self.__nb_errors = 0
        ontoOwlready = None

        try:
            world = or2.World()
            ontoOwlready = world.get_ontology("file://" + filepath)
            ontoOwlready.load(only_local=False)
            self._loaded = True
        except (or2.base.OwlReadyOntologyParsingError, HTTPError, ValueError, TypeError, UnboundLocalError,
                AttributeError):
            self._loaded = False

        if self.isLoaded():
            self.__updateProperties(ontoOwlready)
            self.__updateOwlTriples(ontoOwlready)

    def __updateProperties(self, ontoOwlready: or2.Ontology):
        for clsOwlready in ontoOwlready.classes():
            clsProperties = ClsProperties()
            clsProperties.subClassOf = clsOwlready.is_a
            self._clsProperties[clsOwlready.iri] = clsProperties
        self._clsProperties[Csts.Uris.THING] = ClsProperties()

        individuals = ontoOwlready.individuals()
        for individual in individuals:
            for cls in individual.is_a:
                try:
                    self._clsProperties[cls.iri].nbInstances += 1
                except AttributeError:
                    self.__nb_errors += 1

        for opOwlready in ontoOwlready.object_properties():
            opProperties = OpProperties()
            try:
                opProperties.inverseOf = opOwlready.inverse_property.iri if opOwlready.inverse_property is not None \
                    else Csts.DefaultOpdValues.INVERSE_OF
            except AttributeError:
                self.__nb_errors += 1
            opProperties.isAsymmetric = issubclass(opOwlready, or2.AsymmetricProperty)
            opProperties.isFunctional = issubclass(opOwlready, or2.FunctionalProperty)
            opProperties.isInverseFunctional = issubclass(opOwlready, or2.InverseFunctionalProperty)
            opProperties.isIrreflexive = issubclass(opOwlready, or2.IrreflexiveProperty)
            opProperties.isReflexive = issubclass(opOwlready, or2.ReflexiveProperty)
            opProperties.isSymmetric = issubclass(opOwlready, or2.SymmetricProperty)
            opProperties.isTransitive = issubclass(opOwlready, or2.TransitiveProperty)
            opProperties.label = opOwlready.label if opOwlready.label is not None else Csts.DefaultOpdValues.LABEL
            opProperties.subPropertyOf = [propOwlready.iri for propOwlready in opOwlready.is_a]
            self._opProperties[opOwlready.iri] = opProperties

            for domain_ in opOwlready.domain:
                if domain_ is not None:
                    try:
                        self._clsProperties[domain_.iri].domainOf.append(opOwlready.iri)
                    except AttributeError:
                        self.__nb_errors += 1
            for range_ in opOwlready.range:
                if range_ is not None:
                    try:
                        self._clsProperties[range_.iri].rangeOf.append(opOwlready.iri)
                    except AttributeError:
                        self.__nb_errors += 1

    def __updateOwlTriples(self, ontoOwlready):
        self.__nb_errors = 0
        # Remove duplicates because Owlready2 have errors (ex: for Restrictions on collaborativePizza.owl)
        opsOwlready = rem_duplicates(ontoOwlready.object_properties())
        self._owlTriplesUri = []
        for opOwlready in opsOwlready:
            try:
                domainIRIs = [op_domain.iri for op_domain in opOwlready.domain] if opOwlready.domain != [] else \
                    [Csts.Uris.THING]
                rangeIRIs = [op_range.iri for op_range in opOwlready.range] if opOwlready.range != [] else \
                    [Csts.Uris.THING]
                for domainIRI in domainIRIs:
                    for rangeIRI in rangeIRIs:
                        self._owlTriplesUri.append((domainIRI, opOwlready.iri, rangeIRI))
            except (TypeError, AttributeError):
                self.__nb_errors += 1
        return self._owlTriplesUri
