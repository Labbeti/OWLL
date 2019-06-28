from src.util import iri_to_name
from src.util import split_op_name

import os


class OpData:
    def __init__(self, src: str, iri: str = ""):
        """
            Constructor of OpData.
            :param src: source path of the OP.
            :param iri: iri of the OP.
        """
        self.src = os.path.basename(src)
        self.inverseOfIri = ""
        self.label = ""
        self.domainsIris = []
        self.rangesIris = []
        self.subPropertyOfIris = []
        self.iri = iri
        self.nbInstDomains = []
        self.nbInstRanges = []
        self.asymmetric = False
        self.functional = False
        self.inverseFunctional = False
        self.irreflexive = False
        self.reflexive = False
        self.symmetric = False
        self.transitive = False

    def fromDict(self, d: dict):
        """
            Cast from dict.
            :param d: the source dict where to get the attributes values.
        """
        self.__dict__ = d

    def asDict(self) -> dict:
        """
            Cast to dict.
            :return: the OpData object as a dict.
        """
        return vars(self)

    # Getters
    def getIri(self) -> str:
        return self.iri

    def getDomainsIris(self) -> list:
        return self.domainsIris

    def getDomainsNames(self) -> list:
        return [iri_to_name(iri) for iri in self.getDomainsIris()]

    def getRangesIris(self) -> list:
        return self.rangesIris

    def getRangesNames(self) -> list:
        return [iri_to_name(iri) for iri in self.getRangesIris()]

    def getLabel(self) -> str:
        return self.label

    def getName(self) -> str:
        return iri_to_name(self.iri)

    def getNameSplit(self, filterDomain: bool = False, filterRange: bool = False, filterSubWords: list = None) -> list:
        opNameSplit = split_op_name(self.getName())
        if filterDomain:
            for domainName in self.getDomainsNames():
                opNameSplit = [name for name in opNameSplit if name.lower() != domainName.lower()]
        if filterRange:
            for rangeName in self.getRangesNames():
                opNameSplit = [name for name in opNameSplit if name.lower() != rangeName.lower()]
        if filterSubWords is not None:
            for subWord in filterSubWords:
                opNameSplit = [name for name in opNameSplit if name.lower() != subWord.lower()]
        return opNameSplit

    def getInverseOfIri(self) -> str:
        return self.inverseOfIri

    def getSubPropertyOfIris(self) -> list:
        return self.subPropertyOfIris

    def isAsymmetric(self) -> bool:
        return self.asymmetric

    def isFunctional(self) -> bool:
        return self.functional

    def isInverseFunctional(self) -> bool:
        return self.inverseFunctional

    def isIrreflexive(self) -> bool:
        return self.irreflexive

    def isReflexive(self) -> bool:
        return self.reflexive

    def isSymmetric(self) -> bool:
        return self.symmetric

    def isTransitive(self) -> bool:
        return self.transitive

    def __eq__(self, other) -> bool:
        """
            Equals that ignore the "src" attributes.
            :param other: another OpData to compare.
            :return: True if they represent the same OP.
        """
        return (
            self.inverseOfIri == other.inverseOfIri
            and self.label == other.label
            and self.domainsIris == other.domainsIris
            and self.rangesIris == other.rangesIris
            and self.subPropertyOfIris == other.subPropertyOfIris
            and self.iri == other.iri
            and self.nbInstDomains == other.nbInstDomains
            and self.nbInstRanges == other.nbInstRanges
            and self.asymmetric == other.asymmetric
            and self.functional == other.functional
            and self.inverseFunctional == other.inverseFunctional
            and self.irreflexive == other.irreflexive
            and self.reflexive == other.reflexive
            and self.symmetric == other.symmetric
            and self.transitive == other.transitive
        )

    def __str__(self) -> str:
        """
            Debug function for printing OpData.
            :return: OpData as a string.
        """
        return "%s %s %s %s %s %s  %s %s %s  %d %d %d %d %d %d" % (
            self.iri, self.domainsIris, self.rangesIris, self.subPropertyOfIris, self.inverseOfIri, self.nbInstDomains,
            self.nbInstRanges, self.label, self.asymmetric, self.functional, self.inverseFunctional, self.irreflexive,
            self.reflexive, self.symmetric, self.transitive
        )
