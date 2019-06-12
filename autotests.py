from ontology.Ontology import *
from util import equals
from util import is_obo_op
from util import is_restriction_id
from util import prt
from util import split_input
from util import split_op_name


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
        results = split_op_name(value)
        if results != results_expected:
            raise Exception("Unit test failed: %s != %s " % (results, results_expected))
    prt("OK: test_split_name")


def test_get_object_properties():
    tests = {
        "data/ontologies/tabletopgames.owl",
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
        "data/ontologies/tabletopgames.owl"
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
                prt("Nb instances %s (%d, %d)" % (key, clsPropsOr[key].nbInstances, clsPropsRl[key].nbInstances))
                raise Exception("test_cls_props nbInstances error")

    prt("OK: test_cls_props")


def test_split_input():
    tests = {
        "gengensim results/tests.txt": ["gengensim", "results/tests.txt"],
        "ls -l \"dir\"": ["ls", "-l", "dir"],
        "genopd \"path/with space.txt\" 'bonjour'": ["genopd", "path/with space.txt", "bonjour"],
        "cpp \"l'op '\"": ["cpp", "l'op '"],
        "test 'weirdpath\"": ["test", "weirdpath\""]
    }

    for test, resultsExpected in tests.items():
        results = split_input(test)
        if results != resultsExpected:
            prt("Results = ", results)
            prt("ResultsExpected = ", resultsExpected)
            raise Exception("Unexpected results for split_input")

    prt("OK: test_split_input")


def test_is_obo_op():
    tests = {
        "BFO_0000050": True,
        "RO_000050": True,
        "APOLLO_SV_00001": True,
        "NCIT_R100": True,
        "CIO_0000000": True,
        "MAMO_0000003": True,
        "TR_0004": True,
        "TEDDY_0000176": True,
        "PARTY_IDENTITY": False,
        "IoT_Thing": False,
        "LOMOWL_Record": False,
        "E_Commerce": False,
        "OccurenceA_Premise": False,
    }
    for string, resultExpected in tests.items():
        result = is_obo_op(string)
        if result != resultExpected:
            raise Exception("test_is_obo_op error: %s != %s for %s" % (result, resultExpected, string))

    prt("OK: test_is_obo_op")


def test_is_restriction_id():
    tests = {
        "N0b283aab41a641c1a51c919c8ca0ba44": True,
        "Nc56bae244919441cb660e380a90085ee": True,
        "N8dc00dfa2bf84272b3c852d6c0ab3787": True,
        "NegContainsProperty1_Premise": False,
        "n6b": False,
        "NonarbitraryNeeded_Premise": False,
    }
    for string, resultExpected in tests.items():
        result = is_restriction_id(string)
        if result != resultExpected:
            raise Exception("test_is_restriction_id error")

    prt("OK: test_is_restriction_id")


def test_all():
    prt("Begin autotests.")
    test_split_name()
    test_get_object_properties()
    test_cls_props()
    test_split_input()
    test_is_obo_op()
    test_is_restriction_id()
    prt("OK: All")


if __name__ == "__main__":
    test_all()
