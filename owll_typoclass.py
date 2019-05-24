from ft_fcts import *
from ontology.Ontology import Ontology
from utils import *


def class_with_typo_words():
    filepath_fasttext = "data/fasttext/wiki-news-300d-1M.vec"
    filepath_dbpedia = "data/ontologies/dbpedia_2016-10.owl"
    filepath_results = "results/typoclass/classif.txt"
    limit = 10000

    prt("Classify with typo words on %s...\n" % filepath_dbpedia)
    data, _, dim = load_vectors(filepath_fasttext, limit)
    onto = Ontology(filepath_dbpedia)
    op_names = onto.getObjectProperties()
    out = open(filepath_results, "w", encoding="utf-8")
    out.write("#! Version: %s\n" % get_time())
    out.write("# This file has been generated with %s.\n\n" % filepath_dbpedia)
    out.write("%-7s %-30s %-30s %-10s\n\n" % ("#Found?", "OP name", "Typo word", "Proximity"))

    typo_name, typo_vecs = get_vecs(Config.TYPO_WORDS, data, dim)

    nb_vecs_found = 0
    for name in op_names:
        vec = get_vec(name, data, dim)

        if vec is not None:
            minDist = 10000000
            maxDist = -1
            minWord = "§OWLL_error§"
            for i in range(len(typo_name)):
                typo_word = typo_name[i]
                typo_vec = typo_vecs[i]

                dist = sq_dist(vec, typo_vec)
                if dist > maxDist:
                    maxDist = dist
                if dist < minDist:
                    minDist = dist
                    minWord = typo_word

            out.write("%-7s %-30s %-30s %1.2f\n" % ("OK", name, minWord, 1 - minDist / maxDist))
            nb_vecs_found += 1
        else:
            out.write("%-7s %-30s \n" % ("KO", name))

    out.write(("# Nb vectors found: %d / %d\n" % (nb_vecs_found, len(op_names))))
    out.close()


if __name__ == "__main__":
    class_with_typo_words()
