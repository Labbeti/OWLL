from file_io import *
from matplotlib.font_manager import FontProperties
from ontology.Ontology import Ontology
from sklearn.cluster import *
from sklearn.mixture import GaussianMixture
from util import *

import matplotlib.pyplot as plt
import sklearn as sk


def get_algos(nb_clusters: int) -> list:
    agglo = AgglomerativeClustering(n_clusters=nb_clusters)
    birch = Birch(n_clusters=nb_clusters)
    gauss = GaussianMixture(n_components=nb_clusters)
    kmeans = KMeans(n_clusters=nb_clusters)
    miniBatch = MiniBatchKMeans(n_clusters=nb_clusters)
    spectral = SpectralClustering(n_clusters=nb_clusters)
    affinity = AffinityPropagation()
    meanshift = MeanShift()  # bandwidth=1.25

    algorithms = [
        ("AgglomerativeClustering", agglo),
        ("Birch", birch),
        ("GaussianMixture", gauss),
        ("KMeans", kmeans),
        ("MiniBatchKMeans", miniBatch),
        ("SpectralClustering", spectral),
        ("AffinityPropagation", affinity),
        ("MeanShift", meanshift),
    ]
    return algorithms


def get_partition(nbClusters: int, preds: np.array, opNames: list, opVecs: np.array, dim: int):
    clusters = [[] for _ in range(nbClusters)]
    clustersCenters = np.array([np.zeros(dim) for _ in range(nbClusters)])
    i = 0
    for pred in preds:
        clusters[pred].append(opNames[i])
        clustersCenters[pred] += opVecs[i]
        i += 1

    for i in range(nbClusters):
        clustersCenters[i] /= len(clusters[i])
    return clusters, clustersCenters


def get_centers_names(nbClusters: int, preds: np.array, opNames: list, opVecs: np.array):
    indexNearestPt = [-1 for _ in range(nbClusters)]
    minDist = 10000000
    i = 0
    for pred in preds:
        dist = sq_dist(opVecs[i], opVecs[indexNearestPt[pred]])
        if indexNearestPt[pred] == -1 or dist < minDist:
            minDist = dist
            indexNearestPt[pred] = i
        i += 1
    return [(opNames[index] if index != -1 else "UNKNOWN_CENTER_NAME") for index in indexNearestPt]


def draw_results(nbClusters: int, preds: np.array, opVecs: np.array, clustersCenters: np.array):
    pca = sk.decomposition.PCA(n_components=2)
    # Concatenate vectors and clusters centers to reduced all of it.
    allPts = np.concatenate((opVecs, clustersCenters))
    reduced = pca.fit_transform(allPts)
    # Get the vectors and clusters centers reduced.
    vecsReduced = reduced[:len(reduced) - len(clustersCenters)]

    # Duplicate colors if too many clusters
    colors_for_pt = Consts.COLORS[preds % len(Consts.COLORS)]

    font = FontProperties()
    font.set_weight('bold')
    font.set_size(20)

    plt.scatter(vecsReduced[:, 0], vecsReduced[:, 1], s=6, color=colors_for_pt)
    '''
    centersReduced = reduced[-len(clustersCenters):]
    for i in range(nbClusters):
        plt.text(centersReduced[i, 0], centersReduced[i, 1], s=str(i), color=Config.COLORS[i % len(Config.COLORS)],
                 fontproperties=font)
    '''


def clusterize(filepathOnto: str, filepathFt: str, filepathResults: str):
    limit = 30_000
    # nb_clusters_default pour tous les algos sauf MeanShift et AffinityPropagation
    nbClustersDefault = 13

    filenameOnto = os.path.basename(filepathOnto)
    data, nbWords, dim = load_ft_vectors(filepathFt, limit)
    onto = Ontology(filepathOnto)
    allOpNames = onto.getOpNames()
    opNames, opVecs = get_vecs(allOpNames, data, dim)

    prt("Ontologie = %s" % filepathOnto)
    prt("Nb de relations lu par ft = %d / %d" % (len(opVecs), len(onto.getOpNames())))
    prt("Pourcentage de FastText utilisé = %.1f %%" % (100 * limit / nbWords))

    out = create_result_file(filepathResults)

    i = 0
    algorithms = get_algos(nbClustersDefault)
    for algoName, algoObj in algorithms:
        print("§ Computing %s..." % algoName)
        # Compute learning...
        start = time()
        preds = algoObj.fit_predict(opVecs)
        end = time()

        # Computing partition...
        nbClusters = max(preds) + 1
        clusters, clustersCenters = get_partition(nbClusters, preds, opNames, opVecs, dim)
        clustersCentersNames = get_centers_names(nbClusters, preds, opNames, opVecs)

        # Write in file
        nbTooSmallClusters = 0
        # Note: a cluster is small if his proportion is lower than proportionSmall
        proportionSmall = 100 / (nbClusters * 2)
        for j in range(nbClusters):
            proportion = 100 * len(clusters[j]) / len(opVecs)
            if proportion < proportionSmall:
                nbTooSmallClusters += 1

        out.write("Algorithm: %s\n" % algoName)
        out.write("Small clusters = %d (with proportion < %.2f%%)\n" % (nbTooSmallClusters, proportionSmall))
        out.write("Total clusters = %d\n" % nbClusters)
        out.write("%-10s %-10s %-10s %-10s\n" % ("N°", "Size", "Part(%)", "Center"))
        for j in range(nbClusters):
            proportion = 100 * len(clusters[j]) / len(opVecs)
            out.write("%-10s %-10s %-10s %-10s\n" % (str(j), str(len(clusters[j])), "%.2f" % proportion,
                                                     clustersCentersNames[j]))
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
        plt.suptitle("Clusterisation des noms de \"%s\"" % filenameOnto)
        draw_results(nbClusters, preds, opVecs, clustersCenters)
        i += 1

    prt("Computing of %d algorithms done." % len(algorithms))
    out.close()
    plt.show()
    plt.close()


# Clusterisation of object properties names.
def clust_op_names(_: list = None) -> int:
    clusterize(Consts.Path.File.DBPEDIA, Consts.Path.File.FASTTEXT, Consts.Path.File.Result.CLUST)
    return 0


if __name__ == "__main__":
    clust_op_names()
