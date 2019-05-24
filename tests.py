from ontology.Ontology import *


def test_load():
    filepath = "data/ontologies/tabletopgames_V3 - Copie.owl"
    onto = Ontology(filepath, LoadType.FORCE_RDFLIB)
    op = onto.getObjectProperties()
    triples = onto.getOWLTriples()
    print(triples)
    print(len(op))
    print(len(triples))


if __name__ == "__main__":
    test_load()
