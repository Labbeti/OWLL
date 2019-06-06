from file_io import create_result_file
from owll_opd import read_opd
from sklearn.cluster import AgglomerativeClustering, KMeans
from time import time
from typing import TextIO
from util import *

import gensim as gs


def get_names_opd(filepathOPD, filterWords: bool, filterDuplicates: bool) -> (list, list):
    data, _, _ = read_opd(filepathOPD)

    prt("Reading and filtering OPD...")
    opNames = []
    opNamesSplitted = []
    for values in data:
        opName = values["ObjectProperty"]
        opDomain = values["Domain"]
        opRange = values["Range"]

        words = split_name(opName)
        words = str_list_lower(words)
        if filterWords:
            words = [word for word in words if word.lower() != opDomain.lower() and word.lower() != opRange.lower()
                     and word.lower() not in Config.CONNECT_WORDS]

        if len(words) > 0:
            opNames.append(opName)
            opNamesSplitted.append(words)

    if filterDuplicates:
        opNames = rem_duplicates(opNames)
        opNamesSplitted = rem_duplicates(opNamesSplitted)
    return opNames, opNamesSplitted


def get_clusters(nbClusters: int, preds: list, opNamesSplitted: list) -> list:
    clusters = [[] for _ in range(nbClusters)]
    i = 0
    for pred in preds:
        opNameUsed = "".join(opNamesSplitted[i])
        clusters[pred].append(opNameUsed)
        i += 1
    return clusters


def save_clusters(out: TextIO, clusters: list):
    nbVecTotal = sum([len(cluster) for cluster in clusters])
    i = 0
    for cluster in clusters:
        out.write("Cluster %d (%.2f%%, %d/%d)\n" % (i, to_percent(len(cluster), nbVecTotal), len(cluster), nbVecTotal))
        j = 1
        for OPname in cluster:
            out.write("%s, " % OPname)
            if j % 100 == 0:
                out.write("\n")
            j += 1
        out.write("\n\n")
        i += 1
    out.close()


# Clust with Tfidf functions
def gen_dist_matrix() -> np.array:
    filepathOPD = "results/opd/opd.txt"
    filepathMatrix = "results/gensim/distance_matrix.csv"

    OPnames, OPnamesSplitted = get_names_opd(filepathOPD, True, True)

    prt("Init dictionnary and Tfidf model...")
    dictionary = gs.corpora.Dictionary(OPnamesSplitted)
    # dictionary.save("results/gensim/opnames.dict")
    # print(dictionary)
    corpus = [dictionary.doc2bow(splitted) for splitted in OPnamesSplitted]
    model = gs.models.TfidfModel(corpus)

    prt("Compute distance matrix... (can take several minutes)")
    start = time()
    distanceMatrix = []
    i = 1
    for splitted in OPnamesSplitted:
        if i % int(len(OPnamesSplitted) / 10) == 0:
            prt("%.1f%% done. (elapsed = %.2fs)" % (round(100 * i / len(OPnamesSplitted)), time() - start))
        vec = dictionary.doc2bow(splitted)

        index = gs.similarities.SparseMatrixSimilarity(model[corpus], num_features=len(dictionary))
        sims = index[model[vec]]
        similarities_by_op = list(enumerate(sims))
        dist_vals = [1 - sim for (_, sim) in similarities_by_op]
        # print(dist_vals)
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
    filepathOPD = Config.PATH.FILE.OPD
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
    data, _, _ = read_opd(filepathOPD)
    OPnames, _ = get_names_opd(filepathOPD, True, True)
    clusters = get_clusters(nbClusters, labels, OPnames)
    out = create_result_file(filepathClusters)
    save_clusters(out, clusters)
    prt("Clusters saved in \"%s\"." % filepathClusters)


# Clust with Doc2Vec functions
def gen_doc2vec_clusters(nbClusters: int, filepathClusters: str, filterWords: bool, filterDuplicates: bool):
    filepathOPD = "results/opd/opd.txt"
    opNames, opNamesSplitted = get_names_opd(filepathOPD, filterWords, filterDuplicates)
    prt("Trying clust with %d opNames and %d opNames non empty" % (len(opNames), len(opNamesSplitted)))

    prt("Testing with Doc2Vec... (filterWords=%s, filterDuplicates=%s)" % (filterWords, filterDuplicates))
    documents = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(opNamesSplitted)]
    model = gs.models.Doc2Vec(documents)
    # vector = model.infer_vector(["shutter", "speed"])
    # print("DEBUG = ", vector.shape)

    i = 0
    vecs = np.zeros((len(opNamesSplitted), 100))
    for splitted in opNamesSplitted:
        vec = model.infer_vector(splitted)
        vecs[i] = vec
        i += 1

    prt("Compute %s..." % "KMeans")
    kmeans = KMeans(n_clusters=nbClusters)
    preds = kmeans.fit_predict(vecs)

    prt("Compute done. Saving clusters in \"%s\"." % filepathClusters)
    clusters = get_clusters(nbClusters, preds, opNamesSplitted)
    out = create_result_file(filepathClusters)
    out.write("# Note: filterConnectWords=%s, filterDuplicates=%s\n\n" % (filterWords, filterDuplicates))
    save_clusters(out, clusters)


def test_doc2vec(nbClusters: int):
    gen_doc2vec_clusters(nbClusters, "results/gensim/clustersDoc2Vec_1.txt", False, False)
    gen_doc2vec_clusters(nbClusters, "results/gensim/clustersDoc2Vec_2.txt", True, False)
    gen_doc2vec_clusters(nbClusters, "results/gensim/clustersDoc2Vec_3.txt", False, True)
    gen_doc2vec_clusters(nbClusters, "results/gensim/clustersDoc2Vec_4.txt", True, True)


def gen_gensim_clust(_: str = ""):
    test_doc2vec(13)


if __name__ == "__main__":
    # test_tfidf(13, False)
    test_doc2vec(13)
