from ontology.Ontology import *
from util import equals
from util import prt
from util import split_name


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
        "Permission_Procedure": ["Permission", "Procedure"],
        "mitigated_By": ["mitigated", "By"],
    }
    for value, results_expected in tests.items():
        results = split_name(value)
        if results != results_expected:
            raise Exception("Unit test failed: %s != %s " % (results, results_expected))
    prt("OK: test_split_name")


def test_get_object_properties():
    tests = {
        "data/ontologies/tabletopgames_V3.owl",
        "data/ontologies/dbpedia_2016-10.owl",
        "data/ontologies/collaborativePizza.owl",
        "data/ontologies/lom.owl",
        "data/ontologies/STIX.owl",
        "data/ontologies/DUL.owl",
    }

    for filepath in tests:
        ontoOr = OwlreadyOntology(filepath)
        ontoRl = RdflibOntology(filepath)

        if ontoOr.isLoaded() and ontoRl.isLoaded():
            names_owlready = ontoOr.getOpNames()
            triples_owlready = ontoOr.getOwlTriplesUri()
            names_rdflib = ontoRl.getOpNames()
            triples_rdflib = ontoRl.getOwlTriplesUri()

            if not equals(names_owlready, names_rdflib) or not equals(triples_owlready, triples_rdflib):
                raise Exception("§ Unit test failed for %s, sizes: \n\tOwlReady2: nb_names=%d nb_triples=%d\n\t"
                                "Rdflib: nb_names=%d nb_triples=%d" % (filepath, len(names_owlready),
                                                                       len(triples_owlready), len(names_rdflib),
                                                                       len(triples_rdflib)))
    prt("OK: test_get_object_properties")


def test_cls_props():
    tests = {
        "data/ontologies/tabletopgames_V3.owl"
    }
    for filepath in tests:
        ontoOr = OwlreadyOntology(filepath)
        ontoRl = RdflibOntology(filepath)
        clsPropsOr = ontoOr.getAllClsProperties()
        clsPropsRl = ontoRl.getAllClsProperties()

        if clsPropsOr.keys() != clsPropsRl.keys():
            raise Exception("test_cls_props keys length error")

        for key in clsPropsOr.keys():
            if clsPropsOr[key].nbInstances != clsPropsRl[key].nbInstances:
                raise Exception("test_cls_props nbInstances error")

    prt("OK: test_cls_props")


def test_all():
    prt("Begin autotests.")
    test_split_name()
    test_get_object_properties()
    test_cls_props()
    prt("OK: All")


if __name__ == "__main__":
    test_all()
