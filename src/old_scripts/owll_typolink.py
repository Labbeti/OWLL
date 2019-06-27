from src.CST import CST
from src.file_io import *
from src.models.ontology import OwlreadyOntology
from src.util import get_vec
from src.util import get_vecs
from src.util import prt
from src.util import sq_dist


def class_with_typo_words(filepathFt: str, filepathOnto: str, filepathResults: str):
    """
        Try to classify names with FastText by searching the nearest vector of link words for each vector of OP name.
        :param filepathFt: filepath to FastText vectors CSV file.
        :param filepathOnto: filepath to ontology.
        :param filepathResults: filepath to classifications result file.
    """
    limit = 10000

    prt("Classify with typo words on %s..." % filepathOnto)
    data, _, dim = load_ft_vectors(filepathFt, limit)
    # Get FT vectors for typo words
    typoNames, typoVecs = get_vecs(CST.LINK_WORDS, data, dim)

    prt("Reading ontology \"%s\"..." % filepathOnto)
    onto = OwlreadyOntology(filepathOnto)
    opNames = onto.getOpNames()

    fOut = create_result_file(filepathResults, filepathOnto)
    fOut.write("%-7s %-30s %-30s %-10s\n\n" % ("#Found?", "OP name", "Typo word", "Proximity"))

    prt("Classifying with typo link words...")
    nbVecsFound = 0
    for name in opNames:
        # Get FT vector
        vec = get_vec(name, data, dim)

        # If the name has been found, search the nearest vector in typoVecs
        if vec is not None:
            minDist = 10000000
            maxDist = -1
            minWord = "§OWLL_error§"
            for i in range(len(typoNames)):
                typoWord = typoNames[i]
                typoVec = typoVecs[i]

                dist = sq_dist(vec, typoVec)
                if dist > maxDist:
                    maxDist = dist
                if dist < minDist:
                    minDist = dist
                    minWord = typoWord

            fOut.write("%-7s %-30s %-30s %1.2f\n" % ("OK", name, minWord, 1 - minDist / maxDist))
            nbVecsFound += 1
        else:
            fOut.write("%-7s %-30s \n" % ("KO", name))

    fOut.write(("# Nb vectors found: %d / %d\n" % (nbVecsFound, len(opNames))))
    fOut.close()
    prt("Results has been saved in \"%s\"." % filepathResults)


def typolink(_: list = None) -> int:
    """
        Classify names with link words.
        :param _: <Unused> Arguments from OWLL terminal.
        :return: Exit code for OWLL terminal.
    """
    class_with_typo_words(CST.PATH.FASTTEXT, CST.PATH.DBPEDIA, CST.PATH.TYPO_LINK)
    return 0


if __name__ == "__main__":
    typolink()
