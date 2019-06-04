from Config import *
from ontology.AbstractOntology import AbstractOntology
from ontology.ClsProperties import ClsProperties
from ontology.OpProperties import OpProperties
from urllib.error import HTTPError
from util import rem_duplicates

import owlready2 as owl


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
            world = owl.World()
            ontoOwlready = world.get_ontology("file://" + filepath)
            ontoOwlready.load(only_local=False)
            self._loaded = True
        except (owl.base.OwlReadyOntologyParsingError, HTTPError, ValueError, TypeError, UnboundLocalError,
                AttributeError):
            self._loaded = False

        if self.isLoaded():
            self.__updateProperties(ontoOwlready)
            self.__updateOwlTriples(ontoOwlready)

    def __updateProperties(self, ontoOwlready: owl.Ontology):
        for clsOwlready in ontoOwlready.classes():
            clsProperties = ClsProperties()
            clsProperties.subClassOf = clsOwlready.is_a
            self._clsProperties[clsOwlready.iri] = clsProperties

        for opOwlready in ontoOwlready.object_properties():
            opProperties = OpProperties()
            opProperties.inverseOf = opOwlready.inverse_property.iri if opOwlready.inverse_property is not None else \
                Config.OPD_DEFAULT.INVERSE_OF
            opProperties.isAsymmetric = issubclass(opOwlready, owl.AsymmetricProperty)
            opProperties.isFunctional = issubclass(opOwlready, owl.FunctionalProperty)
            opProperties.isInverseFunctional = issubclass(opOwlready, owl.InverseFunctionalProperty)
            opProperties.isIrreflexive = issubclass(opOwlready, owl.IrreflexiveProperty)
            opProperties.isReflexive = issubclass(opOwlready, owl.ReflexiveProperty)
            opProperties.isSymmetric = issubclass(opOwlready, owl.SymmetricProperty)
            opProperties.isTransitive = issubclass(opOwlready, owl.TransitiveProperty)
            opProperties.label = opOwlready.label if opOwlready.label is not None else Config.OPD_DEFAULT.LABEL
            # TODO : find how to get instances of an OP with OR2, it does not seems possible
            opProperties.nbInstances = Config.OPD_DEFAULT.NB_INSTANCES
            opProperties.subPropertyOf = opOwlready.is_a
            self._opProperties[opOwlready.iri] = opProperties

    def __updateOwlTriples(self, ontoOwlready):
        self.__nb_errors = 0
        # Remove duplicates because Owlready2 have errors (ex: for Restrictions on collaborativePizza.owl)
        opsOwlready = rem_duplicates(ontoOwlready.object_properties())
        self._owlTriplesUri = []
        for opOwlready in opsOwlready:
            try:
                domainIRIs = [op_domain.iri for op_domain in opOwlready.domain] if opOwlready.domain != [] else \
                    [Config.URI.THING]
                rangeIRIs = [op_range.iri for op_range in opOwlready.range] if opOwlready.range != [] else \
                    [Config.URI.THING]
                for domainIRI in domainIRIs:
                    for rangeIRI in rangeIRIs:
                        self._owlTriplesUri.append((domainIRI, opOwlready.iri, rangeIRI))
            except (TypeError, AttributeError):
                self.__nb_errors += 1
        return self._owlTriplesUri
