from src.CST import CST
from time import time
from src.util import prt

import gensim as gs
import numpy as np


# Clust with Tfidf functions
def gen_dist_matrix() -> np.array:
    filepathOPD = "results/opd/opd.txt"
    filepathMatrix = "results/gensim/distance_matrix.csv"

    opNames, opNamesSplitted = get_names_opd(filepathOPD, False, True)

    prt("Init dictionnary and Tfidf model...")
    dictionary = gs.corpora.Dictionary(opNamesSplitted)
    # dictionary.save("results/gensim/opnames.dict")
    # print(dictionary)
    corpus = [dictionary.doc2bow(splitted) for splitted in opNamesSplitted]
    model = gs.models.TfidfModel(corpus)

    prt("Compute distance matrix... (can take several minutes)")
    start = time()
    distanceMatrix = []
    for i, splitted in enumerate(opNamesSplitted):
        # Print every 1% a output to inform that the program is still running.
        if (i + 1) % int(len(opNamesSplitted) / 100) == 0:
            prt("%.1f%% done. (elapsed = %.2fs)" % (round(100 * (i + 1) / len(opNamesSplitted)), time() - start))
        vec = dictionary.doc2bow(splitted)

        index = gs.similarities.SparseMatrixSimilarity(model[corpus], num_features=len(dictionary))
        sims = index[model[vec]]
        similarities_by_op = list(enumerate(sims))
        dist_vals = [1 - sim for (_, sim) in similarities_by_op]
        # print(dist_vals)
        distanceMatrix.append(dist_vals)
    end = time()
    prt("Distance matrix done in %.2fs" % (end - start))

    out = open(filepathMatrix, "w", encoding="utf-8")
    out.write("%d %d\n" % (len(distanceMatrix), len(distanceMatrix[0])))
    for line in distanceMatrix:
        for value in line:
            out.write("%f, " % value)
        out.write("\n")
    out.close()
    return distanceMatrix


def read_dist_matrix(filepath: str) -> np.array:
    fIn = open(filepath, "r", encoding="utf-8")
    firstLine = fIn.readline().split(" ")
    shape = (int(firstLine[0]), int(firstLine[1]))
    matrix = np.ndarray(shape, dtype=float)
    i = 0
    for line in fIn:
        if line != "\n" and not line.startswith("#"):
            values = line.split(", ")
            for j in range(shape[1]):
                matrix[i][j] = float(values[j].strip())
            i += 1
    return matrix


def test_tfidf(nbClusters: int, genMatrix: bool):
    filepathOPD = CST.PATH.OPD
    filepathMatrix = "results/gensim/distance_matrix.csv"
    filepathClusters = "results/gensim/clustersTfidf.txt"

    if genMatrix:
        prt("Creating distance matrix...")
        distanceMatrix = gen_dist_matrix()
        prt("Distance matrix created.")
    else:
        prt("Reading distance matrix...")
        distanceMatrix = read_dist_matrix(filepathMatrix)
        prt("Distance matrix readed.")

    prt("Compute %s..." % "AgglomerativeClustering")
    agglo = AgglomerativeClustering(n_clusters=nbClusters, affinity="precomputed", linkage="single")
    labels = agglo.fit_predict(distanceMatrix)

    prt("Compute done. Saving clusters...")
    _, opNamesSplitted = get_names_opd(filepathOPD, False, True)
    clusters = get_clusters(nbClusters, labels, opNamesSplitted)
    out = create_result_file(filepathClusters)
    save_clusters(out, clusters)
    prt("Clusters saved in \"%s\"." % filepathClusters)
