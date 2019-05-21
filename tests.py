
from csv_fcts import *
from matplotlib.font_manager import FontProperties
from Ontology import *
from os.path import join
from sklearn.cluster import *
from sklearn import mixture
from time import time
from utils import *

import matplotlib.pyplot as plt
import sklearn as sk


def _get_vec_composed_word_mean(word: str, data: map, d: int):
    if not word.islower():
        subwords = split_name(word)
        mean = np.zeros(d)
        nb = 0
        for subword in subwords:
            subvec = data.get(subword.lower())
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


# TODO : update if necessary
IGNORED_WORDS: list = ["a", "as", "at", "by", "for", "has", "in", "is", "of", "so", "the", "to"]


def _get_vec_composed_word_max_length(word: str, data: map, d: int):
    if not word.islower():
        subwords = split_name(word)
        max_length = -1
        subvec_chosen = None
        for subword in subwords:
            subvec = data.get(subword.lower())
            if subvec is not None and (len(subwords) == 1 or subword.lower() not in IGNORED_WORDS):
                max_length = len(subword)
                subvec_chosen = subvec
        return subvec_chosen
    else:
        return None


def get_vec(word: str, data: map, d: int) -> np.ndarray:
    word = word.strip()
    vec = data.get(word)
    if vec is not None:
        return vec
    else:
        if word.islower():
            vec = data.get(word.title())
        else:
            vec = data.get(word.lower())
        if vec is not None:
            return vec
        else:
            return _get_vec_composed_word_max_length(word, data, d)


def gen_default_words():
    #owl_file = "data/tabletopgames_V3.owl"
    owl_file = "data/dbpedia_2016-10.owl"
    fasttext_file = "data/wiki-news-300d-1M.vec"

    obj_prop_names = Ontology(owl_file).get_obj_prop_names()

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
    obj_prop_names = Ontology(file_DBpedia).get_obj_prop_names()

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


def get_partition(dim, preds, names, vecs):
    nb_clusters = max(preds) - min(preds) + 1
    groups = [[] for _ in range(nb_clusters)]
    cluster_centers = [np.zeros(dim) for _ in range(nb_clusters)]
    i = 0
    for pred in preds:
        groups[pred].append(names[i])
        cluster_centers[pred] += vecs[i]
        i += 1
    for i in range(nb_clusters):
        cluster_centers[i] /= len(groups[i])

    nearest_pt = [-1 for _ in range(nb_clusters)]
    i = 0
    for pred in preds:
        if nearest_pt[pred] == -1 or sq_dist(cluster_centers[pred], vecs[i]) < sq_dist(cluster_centers[pred], vecs[nearest_pt[pred]]):
            nearest_pt[pred] = i
        i += 1
    cluster_center_names = np.array(names, dtype=str)[nearest_pt]
    return groups, cluster_centers, cluster_center_names


COLORS = np.array([
    '#377eb8', '#ff7f00', '#4daf4a', '#f781bf', '#a65628',
    '#984ea3', '#999999', '#e41a1c', '#dede00', '#000000'
])


def draw_data(vecs, cluster_centers, preds, file):
    nb_clusters = len(cluster_centers)
    pca = sk.decomposition.PCA(n_components=2)
    all_pts = np.concatenate((vecs, cluster_centers))
    reduced = pca.fit_transform(all_pts)
    vec_reduced = reduced[:len(reduced)-len(cluster_centers)]
    centers_reduced = reduced[-len(cluster_centers):]

    # TODO : create new to not duplicate colors
    colors_for_pt = COLORS[preds % len(COLORS)]

    font = FontProperties()
    font.set_weight('bold')
    font.set_size(22)

    for i in range(nb_clusters):
        plt.text(centers_reduced[i, 0], centers_reduced[i, 1], s=str(i), color=COLORS[i % len(COLORS)], fontproperties=font)
    plt.scatter(vec_reduced[:, 0], vec_reduced[:, 1], s=6, color=colors_for_pt)
    plt.title("Clusterisation pour \"%s\" avec %d clusters" % (file, nb_clusters))


def test_learning():
    file = "data/tabletopgames_V3.owl"
    file = "data/WeatherOntology.owl"
    file = "data/dbpedia_2016-10.owl"
    fasttext_file = "data/wiki-news-300d-1M.vec"
    nb_words_read_ft = 30_000

    names = Ontology(file).get_obj_prop_names()
    data_all_w, n_vec, dim = load_vectors(fasttext_file, nb_words_read_ft)

    vecs = []
    names_filtered = []
    names_out = []
    for name in names:
        vec = get_vec(name, data_all_w, dim)
        if vec is not None:
            vecs.append(vec)
            names_filtered.append(name)
        else:
            names_out.append(name)

    nb_clusters = 10  # NOTE: max is currently 10 because we have only 10 differents colors

    agglo = AgglomerativeClustering(n_clusters=nb_clusters)
    affinity = AffinityPropagation()
    birch = Birch(n_clusters=nb_clusters)
    gauss = sk.mixture.GaussianMixture(n_components=nb_clusters)
    kmeans = KMeans(n_clusters=nb_clusters)
    mean_shift = MeanShift()
    mini_batch = MiniBatchKMeans(n_clusters=nb_clusters)
    spectral = SpectralClustering(n_clusters=nb_clusters)

    i = 1
    clustering_algorithms = [
        ("AgglomerativeClustering", agglo),
        ("AffinityPropagation", affinity),
        ("Birch", birch),
        ("GaussianMixture", gauss),
        ("KMeans", kmeans),
        ("MeanShift", mean_shift),
        ("MiniBatchKMeans", mini_batch),
        ("SpectralClustering", spectral),
    ]
    for name, algorithm in clustering_algorithms:
        print("§ Computing %s..." % name)
        start = time()
        preds = algorithm.fit_predict(vecs)
        end = time()
        groups, cluster_centers, cluster_center_names = get_partition(dim, preds, names, vecs)

        print("§ GROUPES :")
        for group in groups:
            print("§ => ", group)
        for j in range(nb_clusters):
            print("§ Groupe %2d: Size: %3d (%d%%), Center: %-25s" % (j, len(groups[j]), 100*len(groups[j])/len(vecs), cluster_center_names[j]))
        # print("§ Nb de relations = %d / %d" % (len(vecs), len(names)))
        # print("§ Fichier = %s" % file)
        # print("§ Pourcentage de FastText utilisé = %.1f %%" % (100 * nb_words_read_ft / n_vec))
        # print("§ Nb de clusters = %d" % nb_clusters)
        # print("§ Nb de noms NON-classifiés = %s / %s" % (len(names_out), len(names)))
        # print("§ Exemple de 5 noms NON-classifiés = ", names_out[0:5])
        # Note: quelques mots non trouvé dans FastText :
        # ['copilote', 'primogenitor', 'sheading', 'coemperor', 'bourgmestre']

        plt.figure(i)
        plt.suptitle("%s in %.2fs" % (name, end - start))
        draw_data(vecs, cluster_centers, preds, file)
        i += 1
    plt.show()
    plt.close()


def main():
    # gen_default_words()
    # test_1()
    # test_learning()
    return


if __name__ == "__main__":
    main()
