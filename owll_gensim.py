from Config import Config
from fileIO import create_result_file
from gensim.models import FastText
from gensim.models import TfidfModel
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.similarities import SparseMatrixSimilarity
from owll_opd import read_opd
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from time import time
from util import prt
from util import split_name
from util import sq_dist

import gensim as gs
import numpy as np


def get_names_opd(filepathOPD):
    data, _, _ = read_opd(filepathOPD)

    prt("Reading and filtering OPD...")
    OPnames = []
    OPnamesSplitted = []
    for values in data:
        OPname = values["ObjectProperty"]
        OPdomain = values["Domain"]
        OPrange = values["Range"]
        OPnames.append(OPname)
        words = [word.lower() for word in split_name(OPname)]
        words = [word for word in words if word != OPdomain.lower() and word != OPrange.lower() and word
                 not in Config.CONNECT_WORDS]
        if len(words) > 0:
            OPnamesSplitted.append(words)
    return OPnames, OPnamesSplitted


def gen_dist_matrix():
    filepathOPD = "results/opd/opd.txt"
    filepathMatrix = "results/gensim/distance_matrix.csv"

    OPnames, OPnamesSplitted = get_names_opd(filepathOPD)

    prt("Init dictionnary and Tfidf model...")
    dictionary = gs.corpora.Dictionary(OPnamesSplitted)
    dictionary.save("results/gensim/opnames.dict")
    # print(dictionary)
    corpus = [dictionary.doc2bow(splitted) for splitted in OPnamesSplitted]
    model = TfidfModel(corpus)

    prt("Compute distance matrix...")
    start = time()
    distanceMatrix = []
    i = 1
    for splitted in OPnamesSplitted:
        if i % int(len(OPnamesSplitted) / 10) == 0:
            prt("%.1f%% done. (elapsed = %.2fs)" % (round(100 * i / len(OPnamesSplitted)), time() - start))
        vec = dictionary.doc2bow(splitted)

        index = SparseMatrixSimilarity(model[corpus], num_features=len(dictionary))
        sims = index[model[vec]]
        similarities_by_op = list(enumerate(sims))
        dist_vals = [1-sim for (_, sim) in similarities_by_op]
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


def read_matrix(filepath: str) -> np.array:
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


def get_clusters(nbClusters, preds, OPnames):
    clusters = [[] for _ in range(nbClusters)]
    i = 0
    for pred in preds:
        clusters[pred].append(OPnames[i])
        i += 1
    return clusters


def save_clusters(filepathClusters, clusters):
    nbVecTotal = sum([len(cluster) for cluster in clusters])
    out = create_result_file(filepathClusters)
    i = 0
    for cluster in clusters:
        out.write("Label %d (%d/%d)\n" % (i, len(cluster), nbVecTotal))
        for OPname in cluster:
            out.write("%s, " % OPname)
        out.write("\n\n")
        i += 1
    out.close()


def try_clust():
    filepathOPD = Config.PATH.FILE.OPD
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

    clusters = get_clusters(nbClusters, labels, OPnames)
    save_clusters(filepathClusters, clusters)


def try_2():
    filepathClusters = "results/gensim/clusters_2.txt"
    filepathOPD = "results/opd/opd.txt"
    OPnames, OPnamesSplitted = get_names_opd(filepathOPD)

    prt("Testing with fasttext...")
    modelFt = FastText(OPnamesSplitted)

    sp1 = OPnamesSplitted[0]
    print(sp1)
    vec = modelFt.wv[sp1]
    print(vec.shape)
    sim = modelFt.wv.most_similar(["shutter", "speed"])
    print("sim = ", sim)


def try_3():
    filepathClusters = "results/gensim/clusters_2.txt"
    filepathOPD = "results/opd/opd.txt"
    OPnames, OPnamesSplitted = get_names_opd(filepathOPD)

    prt("Testing with Doc2Vec...")
    documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(OPnamesSplitted)]
    model = Doc2Vec(documents)
    #vector = model.infer_vector(["shutter", "speed"])
    #print("DEBUG = ", vector.shape)

    i = 0
    vecs = np.zeros((len(OPnamesSplitted), 100))
    for splitted in OPnamesSplitted:
        vec = model.infer_vector(splitted)
        vecs[i] = vec
        i += 1

    nbClusters = 10
    kmeans = KMeans(n_clusters=nbClusters)
    preds = kmeans.fit_predict(vecs)

    clusters = get_clusters(nbClusters, preds, OPnames)
    save_clusters(filepathClusters, clusters)


def gen_gensim_clust(args: str = ""):
    # gen_dist_matrix()
    # try_clust()
    pass


if __name__ == "__main__":
    #gen_gensim_clust()
    try_3()
