from file_io import create_result_file
from OPD import OPD
from sklearn.cluster import AgglomerativeClustering, KMeans
from time import time
from typing import TextIO
from util import *

import gensim as gs


def get_names_opd(filepathOPD: str, filterWords: bool, filterDuplicates: bool) -> (list, list):
    opd = OPD()
    opd.loadFromFile(filepathOPD)

    prt("Reading and filtering OPD...")
    opNames = []
    opNamesSplitted = []
    for opData in opd.getData():
        opName = opData.getName()

        if filterWords:
            words = str_list_lower(opData.getNameSplit(True, True, Csts.Words.getWordsSearched()))
        else:
            words = str_list_lower(opData.getNameSplit())

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
        opNameUsed = "".join([word.title() for word in opNamesSplitted[i]])
        clusters[pred].append(opNameUsed)
        i += 1
    return clusters


def save_clusters(out: TextIO, clusters: list):
    out.write("# Note: nbClusters = %d\n\n" % len(clusters))
    nbVecTotal = sum([len(cluster) for cluster in clusters])
    i = 0
    for cluster in clusters:
        out.write("Cluster %d (%.2f%%, %d/%d)\n" % (i, to_percent(len(cluster), nbVecTotal), len(cluster), nbVecTotal))
        j = 1
        for opName in cluster:
            out.write("%s, " % opName)
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
    i = 1
    for splitted in opNamesSplitted:
        # Print every 1% a output to inform that the program is still running.
        if i % int(len(opNamesSplitted) / 100) == 0:
            prt("%.1f%% done. (elapsed = %.2fs)" % (round(100 * i / len(opNamesSplitted)), time() - start))
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
    filepathOPD = Csts.Paths.OPD
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


# Clust with Doc2Vec functions
def get_doc2vec_vectors(filterWords: bool, filterDuplicates: bool) -> (np.ndarray, list, list):
    filepathOPD = Csts.Paths.OPD
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
    return vecs, opNames, opNamesSplitted


def gen_doc2vec_clusters(nbClusters: int, filepathClusters: str, filterWords: bool, filterDuplicates: bool):
    vecs, _, opNamesSplitted = get_doc2vec_vectors(filterWords, filterDuplicates)
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


def test_doc2vec_extended(nbClusters: int, filepathClusters: str):
    WEIGHT_MATHS_PROPERTIES = 0.01
    WEIGHT_WORDS = 1
    WEIGHT_DOMAIN_RANGE = 0.5
    filterWords = False
    filterDuplicates = True

    filepathOPD = Csts.Paths.OPD
    opd = OPD()
    opd.loadFromFile(filepathOPD)
    opNamesSplitted = []
    properties = []
    entities = []

    for opData in opd.getData():
        isAsym = float(opData.isAsymmetric()) * WEIGHT_MATHS_PROPERTIES
        isFunc = float(opData.isFunctional()) * WEIGHT_MATHS_PROPERTIES
        isInFu = float(opData.isInverseFunctional()) * WEIGHT_MATHS_PROPERTIES
        isIrre = float(opData.isIrreflexive()) * WEIGHT_MATHS_PROPERTIES
        isRefl = float(opData.isReflexive()) * WEIGHT_MATHS_PROPERTIES
        isSymm = float(opData.isSymmetric()) * WEIGHT_MATHS_PROPERTIES
        isTran = float(opData.isTransitive()) * WEIGHT_MATHS_PROPERTIES

        opNameSplitFiltered = str_list_lower(
            opData.getNameSplit(True, True, Csts.Words.getWordsSearched() if filterWords else [])
        )

        ignored = ["Thing"]
        if len(opNameSplitFiltered) > 0:
            opNamesSplitted.append(opNameSplitFiltered)
            properties.append([isAsym, isFunc, isInFu, isIrre, isRefl, isSymm, isTran])

            domAndRan = []
            for domain in opData.getDomainsNames():
                if domain not in ignored and not is_unreadable(domain):
                    domAndRan.append(domain)
            for range_ in opData.getRangesNames():
                if range_ not in ignored and not is_unreadable(range_):
                    domAndRan.append(range_)
            entities.append(domAndRan)

    if filterDuplicates:
        opNamesSplitted = rem_duplicates(opNamesSplitted)
    docOp = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(opNamesSplitted + Csts.LINK_WORDS_CLUSTERS)]
    docEntities = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(entities)]

    model = gs.models.Doc2Vec(docOp, vector_size=100)
    modelEnt = gs.models.Doc2Vec(docEntities, vector_size=100)

    i = 0
    vecs = np.zeros((len(opNamesSplitted), 100 + 100))
    for splitted in opNamesSplitted:
        if (i+1) % 1000 == 0:
            prt("Inferring vectors... (%d/%d): " % (i+1, len(opNamesSplitted)))
        # Note: Default epoch is 5.
        vec = model.infer_vector(splitted, epochs=10) * WEIGHT_WORDS
        vecEnt = modelEnt.infer_vector(entities[i], epochs=10) * WEIGHT_DOMAIN_RANGE
        vec2 = np.concatenate((vec, vecEnt))
        vec3 = np.concatenate((vec2, properties[i]))
        vecs[i] = vec2
        i += 1

    prt("Compute %s..." % "KMeans")
    kmeans = KMeans(n_clusters=nbClusters)
    preds = kmeans.fit_predict(vecs)

    prt("Compute done. Saving clusters in \"%s\"." % filepathClusters)
    clusters = get_clusters(nbClusters, preds, opNamesSplitted)
    out = create_result_file(filepathClusters, opd.getSrcpath(), opd.getVersion())
    out.write("# Note: filterConnectWords=%s, filterDuplicates=%s\n" % (filterWords, filterDuplicates))
    save_clusters(out, clusters)

    #docLW = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(Csts.LINK_WORDS_CLUSTERS)]
    #modelLW = gs.models.Doc2Vec(docOp, vector_size=200)
    vecsClusters = []
    for cluster in Csts.LINK_WORDS_CLUSTERS:
        vecsCluster = []
        for word in cluster:
            nameSplit = str_list_lower(split_op_name(word))
            vec = model.infer_vector(nameSplit, epochs=10)
            vecsCluster.append(vec)
        vecsClusters.append(vecsCluster)

    fTest = create_result_file("results/gensim/test_classif.txt", opd.getSrcpath(), opd.getVersion())
    i = 0
    for splitted in opNamesSplitted:
        vec = model.infer_vector(str_list_lower(splitted), epochs=10)

        jVec = -1
        minSqDist = 1000
        j = 0
        for vecsCluster in vecsClusters:
            for vecCluster in vecsCluster:
                sqDist = sq_dist(vec, vecCluster)
                if sqDist < minSqDist:
                    minSqDist = sqDist
                    jVec = j
            j += 1
        fTest.write("Name %-40s => %-40s\n" % (opd.getData()[i].getName(), Csts.LINK_WORDS_CLUSTERS_NAMES[jVec]))
        i += 1
    fTest.close()


def gen_gensim_clust(_: list = None) -> int:
    nbClusters = 13
    # test_tfidf(nbClusters, False)
    # test_doc2vec(nbClusters)
    test_doc2vec_extended(nbClusters, "results/gensim/clusters_extended.txt")
    return 0


if __name__ == "__main__":
    gen_gensim_clust()
