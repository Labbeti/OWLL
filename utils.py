import numpy as np
from collections import Counter
from Config import Config
from os import listdir
from os.path import isfile, join
from time import strftime


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
    filenames = [f for f in listdir(dirpath) if isfile(join(dirpath, f))]
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
