from ft_fcts import *
from matplotlib.font_manager import FontProperties
from ontology.Ontology import Ontology
from os.path import basename
from sklearn.cluster import *
from sklearn.mixture import GaussianMixture
from utils import *

import matplotlib.pyplot as plt
import sklearn as sk


def get_nb_clusters(preds):
    return max(preds) + 1


def get_algos(nb_clusters: int) -> list:
    agglo = AgglomerativeClustering(n_clusters=nb_clusters)
    birch = Birch(n_clusters=nb_clusters)
    gauss = GaussianMixture(n_components=nb_clusters)
    kmeans = KMeans(n_clusters=nb_clusters)
    mini_batch = MiniBatchKMeans(n_clusters=nb_clusters)
    spectral = SpectralClustering(n_clusters=nb_clusters)
    affinity = AffinityPropagation()
    meanshift = MeanShift()  # bandwidth=1.25

    algorithms = [
        ("AgglomerativeClustering", agglo),
        ("Birch", birch),
        ("GaussianMixture", gauss),
        ("KMeans", kmeans),
        ("MiniBatchKMeans", mini_batch),
        ("SpectralClustering", spectral),
        ("AffinityPropagation", affinity),
        ("MeanShift", meanshift),
    ]
    return algorithms


def get_partition(preds, op_names, op_vecs, dim):
    nb_clusters = get_nb_clusters(preds)
    clusters = [[] for _ in range(nb_clusters)]
    clusters_centers = np.array([np.zeros(dim) for _ in range(nb_clusters)])
    i = 0
    for pred in preds:
        clusters[pred].append(op_names[i])
        clusters_centers[pred] += op_vecs[i]
        i += 1

    for i in range(nb_clusters):
        clusters_centers[i] /= len(clusters[i])
    return clusters, clusters_centers


def get_centers_names(preds, op_names, op_vecs):
    nb_clusters = get_nb_clusters(preds)
    index_nearest_pt = [-1 for _ in range(nb_clusters)]
    minDist = 10000000
    i = 0
    for pred in preds:
        dist = sq_dist(op_vecs[i], op_vecs[index_nearest_pt[pred]])
        if index_nearest_pt[pred] == -1 or dist < minDist:
            minDist = dist
            index_nearest_pt[pred] = i
        i += 1
    return [(op_names[index] if index != -1 else "§ UNKNOWN §") for index in index_nearest_pt]


def draw_results(preds, op_vecs, clusters_centers):
    nb_clusters = get_nb_clusters(preds)
    pca = sk.decomposition.PCA(n_components=2)
    all_pts = np.concatenate((op_vecs, clusters_centers))
    reduced = pca.fit_transform(all_pts)
    vecs_reduced = reduced[:len(reduced) - len(clusters_centers)]
    centers_reduced = reduced[-len(clusters_centers):]

    # Duplicate colors if too many clusters
    colors_for_pt = Config.COLORS[preds % len(Config.COLORS)]

    font = FontProperties()
    font.set_weight('bold')
    font.set_size(20)

    limit_clusters_index = 0

    plt.scatter(vecs_reduced[:, 0], vecs_reduced[:, 1], s=6, color=colors_for_pt)
    for i in range(min(nb_clusters, limit_clusters_index)):
        plt.text(centers_reduced[i, 0], centers_reduced[i, 1], s=str(i), color=Config.COLORS[i % len(Config.COLORS)],
                 fontproperties=font)


# Clusterisation of object properties names.
def clust_op_names():
    filepath_onto = "data/ontologies/dbpedia_2016-10.owl"
    filepath_ft = "data/fasttext/wiki-news-300d-1M.vec"
    filepath_results = "results/clust/clust_op_names.txt"
    limit = 30_000
    # nb_clusters_default pour tous les algos sauf MeanShift et AffinityPropagation
    nb_clusters_default = 13

    filename_onto = basename(filepath_onto)
    data, nbWords, dim = load_vectors(filepath_ft, limit)
    onto = Ontology(filepath_onto)
    op_names = onto.getObjectProperties()
    op_names, op_vecs = get_vecs(op_names, data, dim)

    prt("Ontologie = %s" % filepath_onto)
    prt("Nb de relations lu par ft = %d / %d" % (len(op_vecs), len(onto.getObjectProperties())))
    prt("Pourcentage de FastText utilisé = %.1f %%" % (100 * limit / nbWords))
    out = open(filepath_results, "w", encoding="utf-8")
    out.write("#! Version: %s\n" % get_time())
    out.write("\n")

    i = 0
    algorithms = get_algos(nb_clusters_default)
    for algoName, algoObj in algorithms:
        print("§ Computing %s..." % algoName)
        # Compute learning...
        start = time()
        preds = algoObj.fit_predict(op_vecs)
        end = time()

        # Computing partition...
        nb_clusters = get_nb_clusters(preds)
        clusters, clusters_centers = get_partition(preds, op_names, op_vecs, dim)
        clusters_centers_names = get_centers_names(preds, op_names, op_vecs)

        # Write in file
        nbTooSmallClusters = 0
        proportionSmall = 100 / (nb_clusters * 2)  # TODO : modif ?
        for j in range(nb_clusters):
            proportion = 100 * len(clusters[j]) / len(op_vecs)
            if proportion < proportionSmall:
                nbTooSmallClusters += 1

        out.write("Algorithm: %s\n" % algoName)
        out.write("Small clusters = %d (with proportion < %.2f%%)\n" % (nbTooSmallClusters, proportionSmall))
        out.write("Total clusters = %d\n" % nb_clusters)
        out.write("%-10s %-10s %-10s %-10s\n" % ("N°", "Size", "Part(%)", "Center"))
        for j in range(nb_clusters):
            proportion = 100 * len(clusters[j]) / len(op_vecs)
            out.write("%-10s %-10s %-10s %-10s\n" % (str(j), str(len(clusters[j])), "%.2f" % proportion,
                                                     clusters_centers_names[j]))
        out.write("\n")
        j = 0
        for cluster in clusters:
            # out.write("Cluster %d:\n%s\n" % (j, str(cluster)))
            j += 1

        # Draw data
        plt.figure(int(i / 4))
        plt.subplot(221 + (i % 4))
        plt.title("%s in %.2fs (%d clusters)" % (algoName, end - start, max(preds) + 1))
        # (nb_clusters clusters pour tous sauf MeanShift et AffinityPropagation)
        plt.suptitle("Clusterisation des noms de \"%s\"" % filename_onto)
        draw_results(preds, op_vecs, clusters_centers)
        i += 1

    prt("Computing of %d algorithms done." % len(algorithms))
    out.close()
    plt.show()
    plt.close()


if __name__ == "__main__":
    clust_op_names()
