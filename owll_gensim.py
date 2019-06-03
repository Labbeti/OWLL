from gensim.models import TfidfModel
from gensim.similarities import SparseMatrixSimilarity
from owll_opd import read_opd
from sklearn.cluster import AgglomerativeClustering
from time import time
from util import prt
from util import split_name

import gensim as gs
import numpy as np


def gen_dist_matrix():
    filepathOPD = "results/opd/opd.txt"
    filepathMatrix = "results/gensim/distance_matrix.csv"
    data, _, _ = read_opd(filepathOPD)

    OPnames = []
    OPnamesSplitted = []
    for values in data:
        OPname = values["ObjectProperty"]
        OPnames.append(OPname)
        OPnamesSplitted.append([word.lower() for word in split_name(OPname)])

    dictionary = gs.corpora.Dictionary(OPnamesSplitted)
    dictionary.save("results/gensim/opnames.dict")
    # print(dictionary)

    corpus = [dictionary.doc2bow(splitted) for splitted in OPnamesSplitted]
    tfidf = TfidfModel(corpus)

    prt("Compute distance matrix...")
    start = time()
    distanceMatrix = []
    i = 1
    for splitted in OPnamesSplitted:
        if i % int(len(OPnamesSplitted) / 10) == 0:
            prt("%.1f%% done. (elapsed = %.2fs)" % (round(100 * i / len(OPnamesSplitted)), time() - start))
        vec = dictionary.doc2bow(splitted)

        index = SparseMatrixSimilarity(tfidf[corpus], num_features=len(dictionary))
        sims = index[tfidf[vec]]
        similarities_by_op = list(enumerate(sims))
        dist_vals = [1-sim for (_, sim) in similarities_by_op]
        # print(sims_vals)
        distanceMatrix.append(dist_vals)
        i += 1
    end = time()
    prt("Distance matrix done in %.2fs" % (end - start))

    out = open(filepathMatrix, "w", encoding="utf-8")
    out.write("%d %d\n" % (len(distanceMatrix), len(distanceMatrix[0])))
    for line in distanceMatrix:
        for value in line:
            out.write("%f, " % value)
        out.write("\n")
    out.close()


def read_matrix(filepath: str) -> np.array:
    fIn = open(filepath, "r", encoding="utf-8")
    firstLine = fIn.readline().split(" ")
    shape = (int(firstLine[0]), int(firstLine[1]))
    matrix = np.ndarray(shape, dtype=float)
    i = 0
    for line in fIn:
        values = line.split(", ")
        for j in range(shape[1]):
            matrix[i][j] = float(values[j].strip())
        i += 1
    return matrix


def try_clust():
    filepathOPD = "results/opd/opd.txt"
    filepathMatrix = "results/gensim/distance_matrix.csv"
    filepathClusters = "results/gensim/clusters.txt"
    data, _, _ = read_opd(filepathOPD)

    OPnames = []
    for values in data:
        OPnames.append(values["ObjectProperty"])

    nbClusters = 10
    prt("Reading distance matrix...")
    distanceMatrix = read_matrix(filepathMatrix)
    prt("Distance matrix readed.")

    agglo = AgglomerativeClustering(n_clusters=nbClusters, affinity="precomputed", linkage="single")
    labels = agglo.fit_predict(distanceMatrix)

    clusters = [[] for _ in range(nbClusters)]
    i = 0
    for label in labels:
        clusters[label].append(OPnames[i])
        i += 1

    out = open(filepathClusters, "w", encoding="utf-8")
    i = 0
    for cluster in clusters:
        out.write("Label %d (%d/%d)\n" % (i, len(cluster), len(data)))
        for OPname in cluster:
            out.write("%s, " % OPname)
        out.write("\n\n")
        i += 1
    out.close()


def gen_gensim_clust(args: str = ""):
    # gen_dist_matrix()
    try_clust()


if __name__ == "__main__":
    gen_gensim_clust()
