

class ClsData:
    """
        Class Data
        This class is used to unify the informations about OWL classes with Rdflib and Owlready2.
    """

    def __init__(self, iri: str = ""):
        """
            Constructor of ClsData.
            :param iri: iri of the OWL class.
        """
        self.subClassOfIris = []
        self.domainOfIris = []
        self.rangeOfIris = []
        self.iri = iri
        self.name = ""
        self.nbInstances = 0
