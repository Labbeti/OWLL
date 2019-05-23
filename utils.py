import numpy as np
from os import listdir
from os.path import isfile, join


def rem_empty(string_list: list) -> list:
    res = []
    for v in string_list:
        if v != "":
            res.append(v)
    return res


def sq_dist(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    return np.sum(np.subtract(v1, v2)**2)


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
