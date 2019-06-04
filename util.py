import numpy as np
from collections import Counter
from Config import Config
from os import listdir
from time import strftime

import os.path


# Print function with a prefix to inform an OWLL output.
def prt(*arg):
    if Config.VERBOSE_MODE:
        print(Config.CONSOLE_PREFIX, end='')
        print(*arg)


def sq_dist(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    return np.sum(np.subtract(v1, v2) ** 2)


# 'a list list -> 'a list
def reshape(l: list) -> list:
    res = []
    for sublist in l:
        res += sublist
    return res


def get_filenames(dirpath: str) -> list:
    filenames = [f for f in listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))]
    return filenames


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


def get_time() -> str:
    return strftime("%d/%m/%Y_%H:%M:%S")


# Return true if list contains the same values but not in the same order.
# note: can not use set() comparaison because we want to take into account duplicates values.
def equals(l1: list, l2: list) -> bool:
    c1 = Counter(l1)
    c2 = Counter(l2)
    diff = c1 - c2
    return list(diff.elements()) == []


def rem_duplicates(l: list) -> list:
    return list(set(l))


def rem_empty(string_list: list) -> list:
    res = []
    for v in string_list:
        if v != "":
            res.append(v)
    return res


def to_percent(num: float, denom: float) -> float:
    return 100. * num / denom


def get_vec(name, data, dim):
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


def get_vecs(names, data, dim) -> (list, list):
    names_with_vec = []
    vecs = []
    for name in names:
        vec = get_vec(name, data, dim)
        if vec is not None:
            names_with_vec.append(name)
            vecs.append(vec)
    return names_with_vec, vecs