from ontology.Ontology import *
from utils import equals
from utils import prt
from utils import split_name


def test_split_name():
    tests = {
        "a": ["a"],
        "bonjourToi": ["bonjour", "Toi"],
        "CoucouToi": ["Coucou", "Toi"],
        "blablaB": ["blabla", "B"],
        "IRIT": ["I", "R", "I", "T"],
        "Florence Bannay": ["Florence", "Bannay"],
        "": [],
        "is_family": ["is", "family"],
        "has given name": ["has", "given", "name"],
        " _ truc__ _chose ": ["truc", "chose"],
        "Permission_Procedure": ["Permission", "Procedure"]
    }
    for value, results_expected in tests.items():
        results = split_name(value)
        if results != results_expected:
            raise Exception("Unit test failed: %s != %s " % (results, results_expected))
    prt("OK: test_split_name")


def test_get_object_properties():
    tests = {
        #"data/ontologies/tabletopgames_V3.owl",
        #"data/ontologies/dbpedia_2016-10.owl",
        #"data/ontologies/no_op/AuthorizationRealms.owl",
        #"data/ontologies/collaborativePizza.owl",
        "data/ontologies/Actor.owl"
    }

    for filepath in tests:
        onto_owl = Ontology(filepath, LoadType.FORCE_OWLREADY2)
        onto_rdf = Ontology(filepath, LoadType.FORCE_RDFLIB)

        names_owlready = onto_owl.getObjectProperties()
        triples_owlready = onto_owl.getOWLTriples()
        names_rdflib = onto_rdf.getObjectProperties()
        triples_rdflib = onto_rdf.getOWLTriples()

        if not equals(names_owlready, names_rdflib) or not equals(triples_owlready, triples_rdflib):
            # prt("DEBUG: auto: ", triples_owlready, "\n\n", triples_rdflib)
            raise Exception("§ Unit test failed for %s, sizes: \n\tOwlReady2: nb_names=%d nb_triples=%d\n\t"
                            "Rdflib: nb_names=%d nb_triples=%d" % (filepath, len(names_owlready),
                                                                   len(triples_owlready), len(names_rdflib),
                                                                   len(triples_rdflib)))

    prt("OK: test_get_object_properties")


def test_all():
    prt("Begin autotests.")
    test_split_name()
    test_get_object_properties()
    prt("OK: All")


if __name__ == "__main__":
    test_all()