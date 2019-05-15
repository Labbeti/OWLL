import io
import numpy as np
from owlready2 import *
from time import time


def load_vectors(filename, limit=1000000) -> map:
    file = io.open(filename, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, d = map(int, file.readline().split())
    data = {}
    i = 1
    for line in file:
        if i % 1000 == 0:
            print("DEBUG: Line: ", i, "/", min(n, limit))  # DEBUG
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = list(map(float, tokens[1:]))
        i += 1
        if i >= limit:
            break
    file.close()
    return data


def get_obj_prop_names(onto: Ontology) -> list:
    obj_prop = list(onto.object_properties())
    obj_prop_names = [str(name)[len(onto.name)+1:] for name in obj_prop]
    return obj_prop_names


def save_vectors(names, data, filename):
    file = open(filename, "w")
    n = len(set(names).intersection(set(data.keys())))
    dim = len(list(data.values())[0])
    file.write(str(n) + " " + str(dim) + "\n")  # TODO
    for name in names:
        vector = data.get(name)
        if vector is not None:
            tmp = str(vector)[1:len(str(vector)) - 1]
            tmp = tmp.replace(",", "")
            file.write(name + " " + tmp + "\n")
    file.close()


def sq_dist(v1, v2) -> np.ndarray:
    return np.sum(np.subtract(v1, v2)**2)


# 'a list list -> 'a list
def reshape(l: list) -> list:
    res = []
    for sublist in l:
        res += sublist
    return res


def test():
    #owl_file = "data/tabletopgames_V3.owl"
    owl_file = "data/dbpedia_2016-10.owl"
    fasttext_file = "data/wiki-news-300d-1M.vec"

    onto = get_ontology(owl_file)
    onto.load()
    obj_prop_names = get_obj_prop_names(onto)

    #print(onto.name)
    #print(obj_prop)
    #print(obj_prop_names)

    t1 = time()
    data = load_vectors(fasttext_file)
    t2 = time()
    print("Load time: ", t2 - t1)
    save_vectors(obj_prop_names, data, "data/res2.csv")

    default_words = [
        ["characterize", "identifies", "defined", "depicted", "qualifies", "delineated", "specific", "belongs"],
        [],
        ["includes", "gathered", "collects"],
        ["iscomposedof", "contains", "assimilates"],
        [],
        [],
        ["do", "realizes", "assume", "accomplishes", "executes", "proceeds", "manages", "ensures", "order", "trigger", "causes"],
        ["helps", "contributesto", "collaboratesin", "participatesin", "encourages", "support", "takespartin", "stimulates", "promotes", "increases", "amplifies", "facilitates"],
        ["uses", "makeuseof", "employs", "callsupon"],
        ["aimsto", "islookingfor", "continues", "tendsto", "research", "wishes"],
        ["dependson", "requires", "influence", "determines", "allows", "related", "necessary"],
        ["about", "transforms", "modified", "converts", "trasfficking", "affects", "takecareof", "concerns"],
        ["product", "cause", "causes", "generate", "resultsin", "created", "develops", "deal", "provides"]
    ]
    default_words = reshape(default_words)

    # default_words = ["has", "contains", "is"]
    save_vectors(default_words, data, "data/default_words.csv")


def main():
    #test()
    data_all_w = load_vectors("data/wiki-news-300d-1M.vec", 10000)
    data_def_w = load_vectors("data/default_words.csv")

    onto = get_ontology("data/dbpedia_2016-10.owl")
    onto.load()
    obj_prop_names = get_obj_prop_names(onto)

    nb_links_found = 0
    i = 1
    for name in obj_prop_names:
        vect = data_all_w.get(name)
        print(str(i) + "/" + str(len(obj_prop_names)) + ": ", end='')
        if vect is not None:
            min = 100000000
            max = -1
            keymin = None
            for key, vect_def in data_def_w.items():
                dist = sq_dist(vect, vect_def)
                if dist < min:
                    min = dist
                    keymin = key
                if dist > max:
                    max = dist
            print(name + " =>      \t" + keymin + "  \t(proximité=%1.2f)" % (1-min/max))
            nb_links_found += 1
        else:
            print(name + " =>      \tNon trouvé dans FastText.")
            # print()
        i += 1
    print(nb_links_found, "/", len(obj_prop_names), " correspondances trouvées.")


if __name__ == "__main__":
    main()
