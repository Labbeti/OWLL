from Csts import Csts


# Object Property Characteristics
# This class is used to unify the informations about object properties with Rdflib and Owlready2.
class OpProperties:
    def __init__(self):
        self.inverseOf: str = ""
        self.isAsymmetric: bool = False
        self.isFunctional: bool = False
        self.isInverseFunctional: bool = False
        self.isIrreflexive: bool = False
        self.isReflexive: bool = False
        self.isSymmetric: bool = False
        self.isTransitive: bool = False
        self.label: str = ""
        self.domains: list = []
        self.ranges: list = []
        self.subPropertyOf: list = []
