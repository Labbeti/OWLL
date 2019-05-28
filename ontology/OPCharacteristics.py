# Object Property Properties
class OPCharacteristics:
    def __init__(self):
        self.inverseOf: str = "None"
        self.isAsymmetric: bool = False
        self.isFunctional: bool = False
        self.isInverseFunctional: bool = False
        self.isIrreflexive: bool = False
        self.isReflexive: bool = False
        self.isSymmetric: bool = False
        self.isTransitive: bool = False
        self.nbInstances: int = 0
        self.domains: list = []
        self.ranges: list = []
        self.subPropertyOf: list = []

    # Used for debugging
    def __str__(self) -> str:
        return "(%s, %d, %d, %d, %d, %d, %d, %s)" % (self.inverseOf, self.isFunctional, self.isInverseFunctional,
                                                     self.isReflexive, self.isSymmetric, self.isTransitive,
                                                     self.nbInstances, self.subPropertyOf)
