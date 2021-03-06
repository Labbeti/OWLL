from time import time
from typing import TextIO
from src.util import prt
from src.util import get_time


def create_result_file(outputFilepath: str, inputFilepath: str = "", inputFileVersion: str = "") -> TextIO:
    """
        Write the default header for results .txt files.
        :param outputFilepath:
        :param inputFilepath:
        :param inputFileVersion:
        :return:
    """

    out = open(outputFilepath, "w", encoding="utf-8")
    out.write("#! Version: %s\n" % get_time())
    if inputFilepath != "":
        if inputFileVersion != "":
            out.write("# This file has been generated with the file \"%s\" (version %s)\n" % (
                inputFilepath, inputFileVersion))
        else:
            out.write("# This file has been generated with the file \"%s\"." % inputFilepath)
    out.write("\n")
    return out


def load_ft_vectors(filepath: str, limit: int = 1_000_000) -> (map, int, int):
    """
        OLD FUNCTION
        Load the fasttext vector.
        :param filepath: path to the .vec FastText file.
        :param limit: maximum number of OP readed.
        :return: a dict of vectors, nb elements, dimension of the vectors
    """
    prt("Loading \"%s\"..." % filepath)
    start = time()
    file = open(filepath, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, file.readline().split())
    data = {}
    i = 1
    for line in file:
        if i % 10000 == 0:
            prt("Reading FastText... (line %7d / %7d)" % (i, min(n, limit)))
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = list(map(float, tokens[1:]))
        i += 1
        if i >= limit:
            break
    file.close()
    end = time()
    prt("Load done \"%s\" in %.2fs" % (filepath, end - start))
    return data, n, d


def save_ft_vectors(data, filepath):
    """
        OLD FUNCTION
        Save vectors to a CSV file.
        :param data: dict of vectors to save.
        :param filepath: filepath where to save the vector as CSV.
        :return:
    """
    file = open(filepath, "w")
    n = len(data)
    d = len(list(data.values())[0])  # dim
    file.write("%s %s\n" % (n, d))

    for word, vector in data.items():
        tmp = str(list(vector))
        tmp = tmp[1:len(tmp) - 1]
        tmp = tmp.replace(",", "")
        file.write(word + " " + tmp + "\n")
    file.close()
