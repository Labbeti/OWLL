from Config import Config


# Object Property Characteristics
# This class is used to unify the informations about object properties with Rdflib and Owlready2.
class OPCharacteristics:
    def __init__(self):
        self.inverseOf: str = Config.OPD_DEFAULT.INVERSE_OF
        self.isAsymmetric: bool = False
        self.isFunctional: bool = False
        self.isInverseFunctional: bool = False
        self.isIrreflexive: bool = False
        self.isReflexive: bool = False
        self.isSymmetric: bool = False
        self.isTransitive: bool = False
        self.label: str = Config.OPD_DEFAULT.LABEL
        self.nbInstances: int = 0
        self.domains: list = []
        self.ranges: list = []
        self.subPropertyOf: list = []

    # Used for debug.
    def __str__(self) -> str:
        return "(%s, %d, %d, %d, %d, %d, %d, %s)" % (self.inverseOf, self.isFunctional, self.isInverseFunctional,
                                                     self.isReflexive, self.isSymmetric, self.isTransitive,
                                                     self.nbInstances, self.subPropertyOf)
