from Config import *
from ontology.AbstractOntology import AbstractOntology
from ontology.OPCharacteristics import OPCharacteristics
from urllib.error import HTTPError
from util import rem_duplicates

import owlready2 as or2


# Clean ontology name for each property
# (ex: tabletopgames_V3.contains -> contains)
def _or2_uri_to_name(string: str) -> str:
    index = max(string.rfind("."), string.rfind("#"))
    return string[index + 1:]


class OwlreadyOntology(AbstractOntology):
    # --- PUBLIC ---
    def __init__(self, filepath: str):
        self.__filepath = filepath
        self.__nb_errors = 0
        self.__clCharacteristics = {}
        self.__opCharacteristics = {}
        self.__or2_onto = None
        self.__or2_world = None
        self.__OWLTriples = []

        self.__load(filepath)

    def getName(self, uri: str) -> str:
        return _or2_uri_to_name(uri)

    # Return the number of errors found while reading the ontology.
    def getNbErrors(self) -> int:
        return self.__nb_errors

    # Return names of the OP.
    # Warning: Does not work with some OWL format like Turtle.
    def getObjectProperties(self) -> list:
        objprops = list(self.__or2_onto.object_properties())
        obj_prop_names = [_or2_uri_to_name(objprop.name) for objprop in objprops]
        return rem_duplicates(obj_prop_names)

    # Get the characteristics for an OP.
    def getOPCharacteristics(self, opUri: str) -> OPCharacteristics:
        if opUri in self.__opCharacteristics.keys():
            return self.__opCharacteristics[opUri]
        else:
            raise Exception("Unknown URI %s." % opUri)

    # Return OWL triples.
    def getOWLTriples(self) -> list:
        return self.__OWLTriples

    def isLoaded(self) -> bool:
        return self.__or2_onto is not None

    # --- PRIVATE ---
    def __load(self, filepath: str):
        self.__filepath = filepath
        self.__nb_errors = 0

        try:
            self.__or2_world = or2.World()
            or2_onto = self.__or2_world.get_ontology("file://" + filepath)
            or2_onto.load(only_local=False)
            self.__or2_onto = or2_onto
        except (or2.base.OwlReadyOntologyParsingError, HTTPError, ValueError, TypeError, UnboundLocalError,
                AttributeError):
            self.__or2_onto = None

        if self.isLoaded():
            self.__updateProperties()
            self.__updateOwlTriples()

    def __updateProperties(self):
        OR2_opProps = list(self.__or2_onto.object_properties())

        for OR2_opProp in OR2_opProps:
            opChars = OPCharacteristics()
            opChars.inverseOf = OR2_opProp.inverse_property.iri if OR2_opProp.inverse_property is not None else \
                Config.OPD_DEFAULT.INVERSE_OF
            opChars.isAsymmetric = issubclass(OR2_opProp, or2.AsymmetricProperty)
            opChars.isFunctional = issubclass(OR2_opProp, or2.FunctionalProperty)
            opChars.isInverseFunctional = issubclass(OR2_opProp, or2.InverseFunctionalProperty)
            opChars.isIrreflexive = issubclass(OR2_opProp, or2.IrreflexiveProperty)
            opChars.isReflexive = issubclass(OR2_opProp, or2.ReflexiveProperty)
            opChars.isSymmetric = issubclass(OR2_opProp, or2.SymmetricProperty)
            opChars.isTransitive = issubclass(OR2_opProp, or2.TransitiveProperty)
            opChars.label = OR2_opProp.label if OR2_opProp.label is not None else Config.OPD_DEFAULT.LABEL
            opChars.nbInstances = Config.OPD_DEFAULT.NB_INSTANCES  # TODO : find how to gt instances of an OP with OR2
            opChars.subPropertyOf = [ancestor.iri for ancestor in OR2_opProp.ancestors() if ancestor.iri != OR2_opProp.iri]
            self.__opCharacteristics[OR2_opProp.iri] = opChars

    def __updateOwlTriples(self):
        self.__nb_errors = 0
        # Remove duplicates because Owlready2 have errors (ex: for Restrictions on collaborativePizza.owl)
        ops = rem_duplicates(self.__or2_onto.object_properties())
        self.__OWLTriples = []
        for op in ops:
            try:
                domainIRIs = [op_domain.iri for op_domain in op.domain] if op.domain != [] else [Config.URI.THING]
                rangeIRIs = [op_range.iri for op_range in op.range] if op.range != [] else [Config.URI.THING]
                for domainIRI in domainIRIs:
                    for rangeIRI in rangeIRIs:
                        self.__OWLTriples.append((domainIRI, op.iri, rangeIRI))
            except (TypeError, AttributeError):
                self.__nb_errors += 1
        return self.__OWLTriples
