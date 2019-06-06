import numpy as np
from collections import Counter
from Config import Config
from os import listdir
from time import strftime

import os.path


# Print function with a prefix to inform an OWLL output.
def prt(*arg):
    if Config.VERBOSE_MODE:
        print(Config.TERMINAL_PREFIX, end='')
        print(*arg)


# Return the squared distance between two points.
def sq_dist(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    return np.sum(np.subtract(v1, v2) ** 2)


# 'a list list -> 'a list
def reshape(l: list) -> list:
    res = []
    for sublist in l:
        res += sublist
    return res


# Return the name list of files contained in dirpath.
def get_filenames(dirpath: str) -> list:
    filenames = [f for f in listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))]
    return filenames


# Split an OP name in several words.
def split_name(word: str) -> list:
    res = []
    buf = ""
    for chr in word:
        if chr.isupper():
            if buf != "":
                res.append(buf)
            buf = chr
        elif chr == "_" or chr == " " or chr == "-":
            if buf != "":
                res.append(buf)
            buf = ""
        else:
            buf += chr
    if buf != "":
        res.append(buf)
    return res


# Return the current time with a specific format for OWLL.
def get_time() -> str:
    return strftime("%d/%m/%Y_%H:%M:%S")


# Return true if list contains the same values but not in the same order.
# note: can not use set() comparaison because we want to take into account duplicates values.
def equals(l1: list, l2: list) -> bool:
    c1 = Counter(l1)
    c2 = Counter(l2)
    diff = c1 - c2
    return list(diff.elements()) == []


# Remove the duplicates in a list.
def rem_duplicates(l: list) -> list:
    res = []
    for elt in l:
        if elt not in res:
            res.append(elt)
    return res


# Remove the empty strings in a string list.
def rem_empty(string_list: list) -> list:
    res = []
    for v in string_list:
        if v != "":
            res.append(v)
    return res


# Return the percentage of num in denum.
def to_percent(num: float, denum: float) -> float:
    return 100. * num / denum


# Return a vector of dimension dim related to name in data.
def get_vec(name: str, data: dict, dim: int) -> np.array:
    words = split_name(name)
    vecs = [(word.lower(), data.get(word.lower())) for word in words]
    vec_res = np.zeros(dim)
    nb_vecs_added = 0
    for word, vec in vecs:
        if vec is not None and (word not in Config.CONNECT_WORDS or len(vecs) == 1):
            vec_res += vec
            nb_vecs_added += 1

    if nb_vecs_added > 0:
        return vec_res / nb_vecs_added
    else:
        return None


# Return the list of names where we can find a vector with the list of vectors found in data.
def get_vecs(names: list, data: dict, dim: int) -> (list, list):
    names_with_vec = []
    vecs = []
    for name in names:
        vec = get_vec(name, data, dim)
        if vec is not None:
            names_with_vec.append(name)
            vecs.append(vec)
    return names_with_vec, vecs


# Split the string to find the list of OWLL terminal arguments.
def split_input(string: str, separator: str) -> list:
    args = string.split(separator)
    args = [arg.strip() for arg in args if arg.strip() != ""]
    return args


# Convert all string in list to lower
def str_list_lower(l: list) -> list:
    return [s.lower() for s in l]
