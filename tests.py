
from csv_fcts import *
from matplotlib.font_manager import FontProperties
from onto_classes.Ontology import *
from sklearn.cluster import *
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


def _get_vec_composed_word_max_length(word: str, data: map, d: int):
    if not word.islower():
        subwords = split_name(word)
        max_length = -1
        subvec_chosen = None
        for subword in subwords:
            subvec = data.get(subword.lower())
            if subvec is not None and (len(subwords) == 1 or subword.lower() not in Config.CONNECT_WORDS):
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

    names = Ontology(file).get_op()
    data_all_w, n_vec, dim = load_vectors(fasttext_file, nb_words_read_ft)

    nb_clusters = 10  # NOTE: max is currently 10 because we have only 10 differents colors

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

    agglo = AgglomerativeClustering(n_clusters=nb_clusters)
    affinity = AffinityPropagation()
    birch = Birch(n_clusters=nb_clusters)
    gauss = sk.mixture.GaussianMixture(n_components=nb_clusters)
    kmeans = KMeans(n_clusters=nb_clusters)
    meanshift = MeanShift()
    mini_batch = MiniBatchKMeans(n_clusters=nb_clusters)
    spectral = SpectralClustering(n_clusters=nb_clusters)

    i = 1
    clustering_algorithms = [
        ("AgglomerativeClustering", agglo),
        ("AffinityPropagation", affinity),
        ("Birch", birch),
        ("GaussianMixture", gauss),
        ("KMeans", kmeans),
        ("MeanShift", meanshift),
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


def test_load():
    filepath = "data/ontologies/boardgameontology.owl"
    onto = Ontology(filepath, LoadType.FORCE_RDFLIB)
    op = onto.getObjectProperties()
    triples = onto.getOWLTriples()
    print(triples)
    print(len(op))
    print(len(triples))


def main():
    # gen_default_words()
    # test_1()
    # test_learning()
    test_load()
    return


if __name__ == "__main__":
    main()
