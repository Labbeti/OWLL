
from csv_fcts import *
from sklearn.cluster import KMeans
from time import time
from utils import *

import owlready2 as owl
import sklearn as sk


def split_name(word: str) -> list:
    res = []
    buf = ""
    for chr in word:
        if chr.isupper():
            if buf != "":
                res.append(buf)
                buf = chr
        else:
            buf += chr
    if buf != "":
        res.append(buf)
    return res


def get_vec(word: str, data: map, d: int) -> np.ndarray:
    vec = data.get(word.lower())
    if vec is not None:
        return vec
    else:
        if not word.islower():
            subwords = split_name(word)
            mean = np.zeros(d)
            nb = 0
            for subword in subwords:
                subvec = get_vec(subword, data, d)
                if subvec is not None:
                    mean += subvec
                    nb += 1
            if nb != 0:
                mean /= nb
                return mean
            else:
                return None
        else:
            return None


def gen_default_words():
    #owl_file = "data/tabletopgames_V3.owl"
    owl_file = "data/dbpedia_2016-10.owl"
    fasttext_file = "data/wiki-news-300d-1M.vec"

    onto = owl.get_ontology(owl_file)
    onto.load()
    obj_prop_names = get_obj_prop_names(onto)

    #print(onto.name)
    #print(obj_prop)
    #print(obj_prop_names)

    t1 = time()
    data, n, d = load_vectors(fasttext_file)
    t2 = time()
    print("Load time: ", t2 - t1)
    #save_vectors(obj_prop_names, data, "data/res2.csv")

    """
    default_words = [
        ["characterize", "isSpecificTo", "identifies", "defined", "depicted", "qualifies", "delineated", "specific", "belongs"],
        ["isA", "illustrationOf", "famous", "higlights", "testifiedTo", "isAnAspectOf", "remindsMeOf", "isAnExampleOf"],
        ["includes", "gathered", "collects"],
        ["isComposedOf", "contains", "assimilates"],
        ["preceding", "comesBefore", "pre-existsAt", "isAPrerequisiteFor", "isPriorTo", "lead", "continuesWith", "isContinuedBy", "endsWith", "isAtTheOriginOf", "isReplacedBy", "isTheFatherOf"],
        ["isSmallerThan", "isLessThan", "isWorseThan", "isExceededBy"],
        ["do", "realizes", "assume", "accomplishes", "executes", "proceeds", "manages", "ensures", "order", "trigger", "causes"],
        ["helps", "contributesTo", "collaboratesIn", "participatesIn", "encourages", "support", "takespartIn", "stimulates", "promotes", "increases", "amplifies", "facilitates"],
        ["uses", "makeUseOf", "employs", "callsUpon", "hasAtItsDisposal"],
        ["aimsTo", "isLookingFor", "continues", "tendsTo", "research", "wishes"],
        ["dependsOn", "requires", "influence", "determines", "allows", "related", "necessary"],
        ["about", "transforms", "modified", "converts", "trafficking", "affects", "takeCareOf", "concerns"],
        ["product", "cause", "causes", "generate", "resultsIn", "created", "develops", "deal", "provides"]
    ]
    """
    default_words = [
        ["characterize", "identifies", "defined", "depicted", "qualifies", "delineated", "specific", "belongs"],
        [],
        ["includes", "gathered", "collects"],
        ["isComposedOf", "contains", "assimilates"],
        [],
        [],
        ["do", "realizes", "assume", "accomplishes", "executes", "proceeds", "manages", "ensures", "order", "trigger",
         "causes"],
        ["helps", "contributesTo", "collaboratesIn", "participatesIn", "encourages", "support", "takesPartIn",
         "stimulates", "promotes", "increases", "amplifies", "facilitates"],
        ["uses", "makeUseOf", "employs", "callsUpon"],
        ["aimsTo", "isLookingFor", "continues", "tendsto", "research", "wishes"],
        ["dependsOn", "requires", "influence", "determines", "allows", "related", "necessary"],
        ["about", "transforms", "modified", "converts", "trafficking", "affects", "takeCareOf", "concerns"],
        ["product", "cause", "causes", "generate", "resultsIn", "created", "develops", "deal", "provides"]
    ]
    default_words = reshape(default_words)

    # default_words = ["has", "contains", "is"]
    data2 = {}
    for word in default_words:
        if word.islower():
            if data.get(word) is not None:
                data2[word] = data.get(word)
        else:
            vec = get_vec(word, data, d)
            if vec is not None:
                data2[word] = vec
    save_vectors(data2, "data/default_words.csv")


def test_1():
    nb_words_read_ft = 10_000
    data_all_w, nAll, dAll = load_vectors("data/wiki-news-300d-1M.vec", nb_words_read_ft)
    data_def_w, _, _ = load_vectors("data/default_words.csv")

    file_DBpedia = "data/dbpedia_2016-10.owl"
    file_foaf = "data/foaf.owl"
    onto = owl.get_ontology(file_DBpedia)
    onto.load()
    obj_prop_names = get_obj_prop_names(onto)

    nb_links_found = 0
    i = 1
    for name in obj_prop_names:
        # vec = data_all_w.get(name)
        vec = get_vec(name, data_all_w, dAll)
        decomp = str(split_name(name))
        print("%4d/%4d: " % (i, len(obj_prop_names)), end='')
        if vec is not None:
            min = 100_000_000
            max = -1
            keymin = None
            for key, vect_def in data_def_w.items():
                dist = sq_dist(vec, vect_def)
                if dist < min:
                    min = dist
                    keymin = key
                if dist > max:
                    max = dist
            print("OK %30s => %-30s (proximité=%1.2f)\t(decomposition=%s)" % (name, keymin, 1-min/max, decomp))
            nb_links_found += 1
        else:
            print("KO %30s => Non trouvé dans FastText. \t(decomposition=%s)" % (name, decomp))
            # print()
        i += 1
    print("%d/%d correspondances trouvées pour les %d premiers mots de FT." % (nb_links_found, len(obj_prop_names), nb_words_read_ft))


def test_learning():
    file_DBpedia = "data/dbpedia_2016-10.owl"
    onto = owl.get_ontology(file_DBpedia)
    onto.load()
    obj_prop_names = get_obj_prop_names(onto)

    nb_words_read_ft = 10_000
    data_all_w, nAll, dAll = load_vectors("data/wiki-news-300d-1M.vec", nb_words_read_ft)

    vecs = []
    obj_prop_names_filtered = []
    for name in obj_prop_names:
        vec = get_vec(name, data_all_w, dAll)
        if vec is not None:
            vecs.append(vec)
            obj_prop_names_filtered.append(name)

    nb_clusters = 10
    preds_kmeans = KMeans(n_clusters=nb_clusters).fit_predict(vecs)

    groups = [[] for _ in range(nb_clusters)]
    i = 0
    for pred in preds_kmeans:
        name = obj_prop_names_filtered[i]
        groups[pred].append(name)
        i += 1
    for group in groups:
        print(group, "\n")

    print("Nb de clusters: %d" % nb_clusters)
    print("Nb de noms non-classifiés: %s / %s" % (len(obj_prop_names) - len(obj_prop_names_filtered), len(obj_prop_names)))


def main():
    # gen_default_words()
    # test_1()
    test_learning()


if __name__ == "__main__":
    main()
