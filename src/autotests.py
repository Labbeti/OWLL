"""
    Test module for several functions of OWLL.
"""

import os

from src.CST import CST
from src.models.ontology.OPD import OPD
from src.models.ontology.OwlreadyOntology import OwlreadyOntology
from src.models.ontology.RdflibOntology import RdflibOntology
from src.TenseDetector import TenseDetector
from src.util import unordered_list_equals
from src.util import is_obo_op
from src.util import is_restriction_id
from src.util import prt
from src.util import split_input
from src.util import split_op_name


def test_split_name():
    """
        Test "split_name" function.
    """
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
    """
        Test of ontologies classes.
    """
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
            dataOr = ontoOr.getAllOpsData()
            names_rdflib = ontoRl.getOpNames()
            dataRl = ontoRl.getAllOpsData()

            if not unordered_list_equals(names_owlready, names_rdflib) or not dataOr == dataRl:
                raise Exception(
                    "§ Unit test failed for %s, sizes: \n\tOwlReady2: nb_names=%d nb_triples=%d\n\tRdflib: "
                    "nb_names=%d nb_triples=%d" % (
                        filepath, len(names_owlready), len(dataOr), len(names_rdflib), len(dataRl)))
    prt("OK: test_get_object_properties")


def test_cls_props():
    """
        Test 2 of ontologies classes.
    """
    tests = {
        "data/ontologies/tabletopgames.owl"
    }
    for filepath in tests:
        ontoOr = OwlreadyOntology(filepath)
        ontoRl = RdflibOntology(filepath)
        clsPropsOr = ontoOr.getAllClsData()
        clsPropsRl = ontoRl.getAllClsData()

        if clsPropsOr.keys() != clsPropsRl.keys():
            raise Exception("test_cls_props keys length error")

        for key in clsPropsOr.keys():
            if clsPropsOr[key].nbInstances != clsPropsRl[key].nbInstances:
                prt("Nb instances %s (%d, %d)" % (key, clsPropsOr[key].nbInstances, clsPropsRl[key].nbInstances))
                raise Exception("test_cls_props nbInstances error")

    prt("OK: test_cls_props")


def test_split_input():
    """
        Test "split_input" function.
    """
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
    """
        Test "is_obo_op" function.
    """
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
    """
        Test "is_restriction_id" function.
    """
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


def test_save_load_opd():
    """
        Test OPD class.
    """
    filepath = CST.PATH.OPD
    filepathCopy = os.path.join(os.path.dirname(filepath), "opd_copy.txt")

    opd = OPD()
    opd.loadFromFile(filepath)
    opd.saveInFile(filepathCopy, False)
    opdCopy = OPD()
    opdCopy.loadFromFile(filepathCopy)

    os.remove(filepathCopy)
    if opd != opdCopy:
        d1 = opd.getData()
        d2 = opdCopy.getData()
        if len(d1) != len(d2):
            raise Exception("OPD has not the same number of op data.")

        for i in range(len(d1)):
            if d1[i] != d2[i]:
                raise Exception("Foudn distincts op: ", d1[i].iri, d2[i].iri)
        raise Exception("test_save_load_opd opd error")

    prt("OK: test_save_load_opd")


def test_tense_verb():
    """
        Test TenseDetector class.
    """
    tests = {
        "added": ("add", ["past", "past participle"]),
        "taken": ("take", ["past participle"]),
    }

    filepathVerbsConj = "data/verb_conj.txt"
    detector = TenseDetector()
    detector.load(filepathVerbsConj)
    for verb, (expectedInfVerb, expectedTense) in tests.items():
        (infVerb, tense) = detector.recognize(verb)
        if expectedInfVerb != infVerb or expectedTense != tense:
            print("Error: %s != %s or %s != %s" % (expectedInfVerb, infVerb, expectedTense, tense))
            raise Exception("test_tense_verb error")
    prt("OK: test_tense_verb")


def test_all():
    """
        Run all tests.
    """
    prt("Begin autotests.")
    test_split_name()
    test_get_object_properties()
    test_cls_props()
    test_split_input()
    test_is_obo_op()
    test_is_restriction_id()
    test_save_load_opd()
    test_tense_verb()
    prt("OK: All")


if __name__ == "__main__":
    test_all()
