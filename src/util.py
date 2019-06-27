"""
    Utility functions module.
"""

import numpy as np
from collections import Counter
from src.CST import CST
from os import listdir
from time import strftime

import os.path
import re


def iri_to_name(iri: str) -> str:
    """
        Clean ontology iri to get the name for each property
        ex: tabletopgames_V3.contains -> contains
        ex: org/ontology/isPartOfWineRegion -> isPartOfWineRegion
        ex: http://semanticweb.org/tabletopgames_V3#contains -> contains
        :param iri: IRI path of the element.
        :return: name found at the end of the IRI.
    """
    if iri == "":
        return ""
    elif iri[-1] == "/":
        iri = iri[:len(iri) - 1]
    index = max(iri.rfind("."), iri.rfind("#"), iri.rfind("/"))
    return iri[index + 1:]


def is_obo_op(name: str) -> bool:
    """
        Check if a name is a OBO name.
        The OBO Foundry contains a lot of op names like "BFO_0000050", there are useless for semantic learning.
        ex: BFO_0000050, RO_000050, APOLLO_SV_00001, NCIT_R100.
        :param name: name to check.
        :return: True if name is an OBO name.
    """
    return bool(re.search(r"^[A-Z_]+_[A-Z0-9]+", name)) and bool(re.search(r"\d", name))


def is_restriction_id(name: str) -> bool:
    """
        Check if a name is a Rdflib id.
        Note: Rdflib generate an id for class only defined by operation like union or intersection of other classes.
        :param name: name to check.
        :return: True if name is a Rdflib id.
    """
    return bool(re.search(r"^N[a-f0-9]+$", name))


def is_unreadable(name: str) -> bool:
    return is_obo_op(name) or is_restriction_id(name)


def prt(*arg):
    """
        Print function with a prefix to inform an OWLL output.
    """
    if CST.VERBOSE_MODE:
        print(CST.TERMINAL_PREFIX, end='')
        print(*arg)


def dbg(*arg):
    if CST.DEBUG_MODE:
        print(CST.TERMINAL_PREFIX + "DEBUG: ", end='')
        print(*arg)


def sq_dist(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """
        Return the squared distance between two points.
        :param v1:
        :param v2:
        :return:
    """
    return np.sum(np.subtract(v1, v2) ** 2)


def dist(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    return np.sqrt(sq_dist(v1, v2))


def reshape(l: list) -> list:
    """
        Reshape dimension of a list of list to a list.
        'a list list -> 'a list
        :param l: 
        :return: 
    """""
    res = []
    for sublist in l:
        res += sublist
    return res


def get_filenames(dirpath: str) -> list:
    """
        Return the name list of files contained in dirpath.
        :param dirpath:
        :return:
    """
    filenames = [f for f in listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))]
    return filenames


def get_filepaths(dirpath: str) -> list:
    """
        Return the name list of files contained in dirpath.
        :param dirpath:
        :return:
    """
    filenames = [os.path.join(dirpath, f) for f in listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))]
    return filenames


def split_op_name(word: str) -> list:
    """
        Split an OP name in several words.
        :param word:
        :return:
    """
    res = []
    buf = ""
    for chr_ in word:
        if chr_.isupper():
            if buf != "":
                res.append(buf)
            buf = chr_
        elif chr_ == "_" or chr_ == " " or chr_ == "-":
            if buf != "":
                res.append(buf)
            buf = ""
        else:
            buf += chr_
    if buf != "":
        res.append(buf)
    return res


def filter_op_name_split(opNameSplit: list, opDomain: str, opRange: str) -> list:
    return [word for word in opNameSplit
            if word.lower() != opDomain.lower()
            and word.lower() != opRange.lower()
            and word.lower() not in CST.WORDS.getWordsSearched()]


def get_time() -> str:
    """
        Return the current time with a specific format for OWLL.
        :return:
    """
    return strftime("%d/%m/%Y_%H:%M:%S")


def unordered_list_equals(l1: list, l2: list) -> bool:
    """
        Return true if list contains the same values but not in the same order.
        Note: can not use set() comparaison because we want to take into account duplicates values.
        :param l1:
        :param l2:
        :return:
    """
    c1 = Counter(l1)
    c2 = Counter(l2)
    diff = c1 - c2
    return list(diff.elements()) == []


def rem_duplicates(l: list) -> list:
    """
        Remove duplicates in a list.
        :param l:
        :return:
    """
    res = []
    for elt in l:
        if elt not in res:
            res.append(elt)
    return res


def rem_empty(string_list: list) -> list:
    """
        Remove the empty strings in a string list.
        :param string_list:
        :return:
    """
    res = []
    for v in string_list:
        if v != "":
            res.append(v)
    return res


def to_percent(num: float, denum: float) -> float:
    """
        Return the percentage of num in denum.
        :param num:
        :param denum:
        :return:
    """
    return 100. * num / denum


def get_vec(name: str, data: dict, dim: int) -> np.array:
    """
        Return a vector of dimension dim related to name in data.
        :param name:
        :param data:
        :param dim:
        :return:
    """
    words = split_op_name(name)
    vecs = [(word.lower(), data.get(word.lower())) for word in words]
    vec_res = np.zeros(dim)
    nb_vecs_added = 0
    for word, vec in vecs:
        if vec is not None and (word not in CST.WORDS.getWordsSearched() or len(vecs) == 1):
            vec_res += vec
            nb_vecs_added += 1

    if nb_vecs_added > 0:
        return vec_res / nb_vecs_added
    else:
        return None


def get_vecs(names: list, data: dict, dim: int) -> (list, list):
    """
        Return the list of names where we can find a vector with the list of vectors found in data.
        :param names:
        :param data:
        :param dim:
        :return:
    """
    names_with_vec = []
    vecs = []
    for name in names:
        vec = get_vec(name, data, dim)
        if vec is not None:
            names_with_vec.append(name)
            vecs.append(vec)
    return names_with_vec, vecs


def split_input(string: str) -> list:
    """
        Split the string to find the list of OWLL terminal arguments.
        Ex: "genopd \"data/dir with spaces/tmp.txt\" -> ["genopd", "data/dir with spaces/tmp.txt"]
        Ex: "genopd \"path'weird ?'\"" -> ["genopd", "path'weird ?'"]
        :param string:
        :return:
    """
    inQuote = False
    inDblQuote = False
    buf = ""
    res = []

    for chr_ in string:
        if chr_ == "\"":
            if inQuote:
                buf += chr_
            else:
                inDblQuote = not inDblQuote
                if buf != "":
                    res.append(buf)
                    buf = ""
        elif chr_ == "'":
            if inDblQuote:
                buf += chr_
            else:
                inQuote = not inQuote
                if buf != "":
                    res.append(buf)
                    buf = ""
        elif chr_ == " ":
            if inDblQuote or inQuote:
                buf += chr_
            elif buf != "":
                res.append(buf)
                buf = ""
        else:
            buf += chr_
    if buf != "":
        res.append(buf)
    return res


def str_list_lower(l: list) -> list:
    """
        Convert all string in list to lower.
        :param l:
        :return:
    """
    return [s.lower() for s in l]


def get_args(args, defaultArgs: list) -> list:
    """
        Return args completed by the defaultArgs list.
        :param args:
        :param defaultArgs:
        :return:
    """
    if args is not None:
        return args + defaultArgs[len(args):]
    else:
        return defaultArgs


def print_command_help(usage: str, desc: str, defaultArgs: list = None):
    print("%-15s: %s" % ("Usage", usage))
    print("%-15s: %s" % ("Description", desc))

    if defaultArgs is not None:
        for (name, value) in defaultArgs:
            print("Default value of \"%s\" is \"%s\"." % (name, value))


def init_cst_from_args(args: list):
    CST.VERBOSE_MODE = "-verbose" in args
    CST.DEBUG_MODE = "-debug" in args
