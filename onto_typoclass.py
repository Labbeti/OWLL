from csv_fcts import *
from onto_classes.Ontology import Ontology
from utils import sq_dist


def class_with_typo_words():
    filepath_fasttext = "data/fasttext/wiki-news-300d-1M.vec"
    filepath_dbpedia = "data/ontologies/dbpedia_2016-10.owl"
    filepath_results = "results/typoclass/classif.txt"
    limit = 10000

    data, _, dim = load_vectors(filepath_fasttext, limit)
    onto = Ontology(filepath_dbpedia)
    op_names = onto.getObjectProperties()
    out = open(filepath_results, 'w', encoding='utf-8')

    typo_name, typo_vecs = get_vecs(op_names, data, dim)

    nb_vecs_found = 0
    for name in op_names:
        vec = get_vec(name, data, dim)

        if vec is not None:
            minDist = 10000000
            maxDist = -1
            minWord = ""
            for i in range(len(typo_name)):
                typo_word = typo_name[i]
                typo_vec = typo_vecs[i]

                dist = sq_dist(vec, typo_vec)
                if dist > maxDist:
                    maxDist = dist
                if dist < minDist:
                    minDist = dist
                    minWord = typo_word

            out.write("OK %30s => %-30s (proximity=%1.2f)\n" % (name, minWord, 1 - minDist / maxDist))
            nb_vecs_found += 1
        else:
            out.write("KO %30s => ?\n" % name)

    out.write(("Nb vectors found: %d / %d\n" % (nb_vecs_found, len(op_names))))
    out.close()


if __name__ == "__main__":
    class_with_typo_words()
