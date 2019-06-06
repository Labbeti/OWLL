

# Class Characteristics
# This class is used to unify the informations about OWL classes with Rdflib and Owlready2.
class ClsProperties:
    def __init__(self):
        self.subClassOf: list = []
        self.domainOf: list = []
        self.rangeOf: list = []
        self.nbInstances: int = 0

    def __eq__(self, other) -> bool:
        return self.subClassOf == other.subClassOf and self.domainOf == other.domainOf and self.rangeOf == \
               other.rangeOf and self.nbInstances == other.nbInstances

    def __str__(self) -> str:
        return "(%s,%s,%s,%d)" % (self.subClassOf, self.domainOf, self.rangeOf, self.nbInstances)
