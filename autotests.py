from tests import split_name
from onto_classes.Ontology import *


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
    print("§ OK: test_split_name")


def test_get_object_properties():
    tests = {
        "data/ontologies/tabletopgames_V3.owl",
        "data/ontologies/dbpedia_2016-10.owl",
        "data/ontologies/no_op/AuthorizationRealms.owl",
        "data/ontologies/TTICarOnto.owl"
    }

    for filepath in tests:
        onto_owl = Ontology(filepath, LoadType.FORCE_OWLREADY2)
        onto_rdf = Ontology(filepath, LoadType.FORCE_RDFLIB)
        names_owlready = onto_owl.get_op()
        names_rdflib = onto_rdf.get_op()
        triples_owlready = onto_owl.get_op()
        triples_rdflib = onto_rdf.get_op()

        if set(names_owlready) != set(names_rdflib) or \
                set(triples_owlready) != set(triples_rdflib):
            raise Exception("Unit test failed: sizes: \n\towlready2: %d %d\n\trdflib: %d %d" %
                            (len(names_owlready), len(triples_owlready), len(names_rdflib), len(triples_rdflib)))

    print("§ OK: test_get_object_properties")


def test_all():
    print("§ Begin autotests.")
    test_split_name()
    test_get_object_properties()
    print("§ OK: All")


if __name__ == "__main__":
    test_all()
