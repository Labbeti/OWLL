from Config import Config
from file_io import *
from ontology.OwlreadyOntology import OwlreadyOntology
from util import get_vec
from util import get_vecs
from util import prt
from util import sq_dist


# Try to classify names with FastText by searching the nearest vector of Connect words for each vector of OP name.
def class_with_typo_words(_: str = ""):
    filepathFT = Config.PATH.FILE.FASTTEXT
    filepathDBpedia = "data/ontologies/dbpedia_2016-10.owl"
    filepathResults = "results/typoclass/classif.txt"
    limit = 10000

    prt("Classify with typo words on %s..." % filepathDBpedia)
    data, _, dim = load_ft_vectors(filepathFT, limit)
    # Get FT vectors for typo words
    typoNames, typoVecs = get_vecs(Config.TYPO_WORDS, data, dim)

    prt("Reading ontology \"%s\"..." % filepathDBpedia)
    onto = OwlreadyOntology(filepathDBpedia)
    opNames = onto.getOpNames()

    fOut = create_result_file(filepathResults, filepathDBpedia)
    fOut.write("%-7s %-30s %-30s %-10s\n\n" % ("#Found?", "OP name", "Typo word", "Proximity"))

    prt("Classifying with typo words...")
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


if __name__ == "__main__":
    class_with_typo_words()
