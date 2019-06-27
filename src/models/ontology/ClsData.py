

class ClsData:
    """
        Class Characteristics
        This class is used to unify the informations about OWL classes with Rdflib and Owlready2.
    """

    def __init__(self, iri: str = ""):
        self.subClassOfIris = []
        self.domainOfIris = []
        self.rangeOfIris = []
        self.iri = iri
        self.name = ""
        self.nbInstances = 0
