from src.file_io import create_result_file

from gensim import corpora
from gensim import models
from gensim import similarities

from graphviz import Digraph

from src.ontology.OwlreadyOntology import OwlreadyOntology
from src.ontology.RdflibOntology import RdflibOntology
from src.old_scripts.owll_gensim import get_names_opd
from sklearn.cluster import KMeans
from src.util import *

import gensim as gs
import matplotlib.pyplot as plt
import numpy as np
import sklearn as sk


def test_load():
    filepath = "data/ontologies/tabletopgames.owl"
    # '''
    onto = OwlreadyOntology(filepath)
    prt("Loaded = %d" % onto.isLoaded())
    for clsIri, clsProp in onto.getAllClsProperties().items():
        prt(clsIri, " = ", clsProp.nbInstances, ", ", clsProp.domainOf, ", ", clsProp.rangeOf)
    # '''
    # '''
    onto = RdflibOntology(filepath)
    prt("Loaded = %d" % onto.isLoaded())
    for clsIri, clsProp in onto.getAllClsProperties().items():
        prt(clsIri, " = ", clsProp.nbInstances)
    # '''


def test_gen_model():
    # fname = get_tmpfile("vectors.kv")  # search in "C:\\Users\\invite\\AppData\\Local\\Temp\\"

    filepath_opd = "results/stats/opd.txt"
    filepath_model = "results/gensim/word2vec.model"
    data, version, _ = read_opd(filepath_opd)

    names = []
    nb_names = 0
    for values in data:
        op_name = values["ObjectProperty"]
        words_name = split_op_name(op_name)
        words_name_lower = [word.lower() for word in words_name]
        names.append(words_name_lower)
        nb_names += len(words_name)

    print("OP = %d\nNames = %d" % (len(names), nb_names))
    # print(filepath_model)
    # model = Word2Vec(names, size=100, window=5, min_count=1, workers=4)
    # model.wv.save(filepath_model)
    '''
    wv = KeyedVectors.load(filepath_model)
    out = open("results/gensim/data_trained.txt", "w", encoding="utf-8")

    out.write("%d %d\n" % (len(wv.vocab), wv.vector_size))
    for word in wv.vocab:
        out.write("%s " % word)
        vector = wv[word]
        for value in vector:
            out.write("%.3f " % value)
        out.write("\n")
    out.close()
    '''

    dictionary = corpora.Dictionary(names)
    dictionary.save("results/gensim/opnames.dict")
    # print(dictionary)

    rems = [["inside"], ["is", "inside"]]
    for rem in rems:
        names = list(filter(lambda op: op != rem, names))
        # names.remove(rem)
    ''' 
    '''

    corpus = [dictionary.doc2bow(text) for text in names]
    # print(corpus)

    tfidf = models.TfidfModel(corpus)

    quitting_w = ["quit", "exit", "QUIT", "EXIT"]
    user_in = ""
    while user_in not in quitting_w:
        # user_in = "is a part of"
        user_in = input("> ")
        if user_in in quitting_w:
            break

        words = user_in.replace("  ", " ").lower().split()
        vec = dictionary.doc2bow(words)
        if len(words) != len(vec):
            print("Err: un mot de \"%s\" n'a pas été trouvé dans le dictionnaire" % user_in)
            return
        print("Test avec ", words, ", ", vec, "\n")

        index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=len(dictionary))
        sims = index[tfidf[vec]]
        similarities_by_op = list(enumerate(sims))
        sims_vals = [1 - sim for (_, sim) in similarities_by_op]
        indexes = np.argsort(sims_vals)

        (ind, sim) = similarities_by_op[indexes[0]]
        print("Similarité (1er) = %.2f (%d)" % (sim, ind))
        print("1er: ", names[indexes[0]])

        print("Similarité (2nd) = %.2f (%d)" % (sim, ind))
        print("2nd: ", names[indexes[1]])


def test_graphviz():
    dot = Digraph(comment='Coucou')
    dot.node('A', 'NomA')
    dot.node('B', 'NomB')
    dot.node('C', 'NomC')

    dot.edges(['AB', 'AC'])
    dot.edge('B', 'C', constraint='false')

    print(dot.source)
    dot.render('indev/coucou.gv', view=True)


def tests_gs_ft():
    filepathOPD = "results/opd/opd.txt"
    opNames, opNamesSplitted = get_names_opd(filepathOPD, False, True)
    prt("Trying clust with %d opNames and %d opNames non empty" % (len(opNames), len(opNamesSplitted)))

    documents = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(opNamesSplitted)]
    model = gs.models.Doc2Vec(documents)

    tests = [
        ["contains"],
        ["is", "contained", "in"],
        ["is", "inside", "of"],
        ["has"],
        ["is", "part", "of"],
    ]

    for i in range(len(tests)):
        t1 = tests[i]
        v1 = model.infer_vector(t1)
        for j in range(i+1, len(tests)):
            t2 = tests[j]
            v2 = model.infer_vector(t2, epochs=10)  # epochs to set the number of learning steps
            prt("(%-30s,%-30s): %f" % (t1, t2, float(sq_dist(v1, v2))))

    '''
    for test in tests:
        ms1 = model.most_similar(test)  # doesnt work with words not in vocabulary
        prt("%-30s => %-30s" % (test, ms1))
    '''


def get_names_opd(filepathOPD: str, filterWords: bool, filterDuplicates: bool) -> (list, list):
    opd = OPD()
    opd.loadFromFile(filepathOPD)

    prt("Reading and filtering OPD...")
    opNamesSplitted = opd.getOpNamesSplit(
        keepEmptyLists=False, filterDomain=filterWords, filterRange=filterWords,
        filterSubWords=CST.WORDS.getWordsSearched() if filterWords else [], filterDuplicates=filterDuplicates)
    return opNamesSplitted


# Clust with Doc2Vec functions
def get_doc2vec_vectors(filterWords: bool, filterDuplicates: bool) -> (np.ndarray, list, list):
    filepathOPD = CST.PATH.OPD
    opNames, opNamesSplitted = get_names_opd(filepathOPD, filterWords, filterDuplicates)
    prt("Trying clust with %d opNames and %d opNames non empty" % (len(opNames), len(opNamesSplitted)))

    prt("Testing with Doc2Vec... (filterWords=%s, filterDuplicates=%s)" % (filterWords, filterDuplicates))
    documents = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(opNamesSplitted)]
    model = gs.models.Doc2Vec(documents)
    # vector = model.infer_vector(["shutter", "speed"])
    # print("DEBUG = ", vector.shape)

    vecs = np.zeros((len(opNamesSplitted), 100))
    for i, splitted in enumerate(opNamesSplitted):
        vec = model.infer_vector(splitted)
        vecs[i] = vec
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


def draw_results(nbClusters: int, preds: np.array, vecs: np.array, clustersCenters: np.array):
    prt("DEBUG: ", np.array(vecs).shape, " ", np.array(clustersCenters).shape)
    pca = sk.decomposition.PCA(n_components=2)
    # Concatenate vectors and clusters centers to reduced all of it.
    allPts = np.concatenate((vecs, clustersCenters))
    reduced = pca.fit_transform(allPts)
    # Get the vectors and clusters centers reduced.
    vecsReduced = reduced[:len(vecs)]

    # Duplicate colors if too many clusters
    colorsByPoints = CST.COLORS[preds % len(CST.COLORS)]

    font = FontProperties()
    font.set_weight('bold')
    font.set_size(20)

    plt.scatter(vecsReduced[:, 0], vecsReduced[:, 1], s=6, color=colorsByPoints)
    '''
    centersReduced = reduced[-len(clustersCenters):]
    for i in range(nbClusters):
        plt.text(centersReduced[i, 0], centersReduced[i, 1], s=str(i), color=Csts.COLORS[i % len(Csts.COLORS)],
                 fontproperties=font)
    # '''


def test_doc2vec_extended(nbClusters: int, filepathClusters: str):
    WEIGHT_MATHS_PROPERTIES = 0.
    WEIGHT_WORDS = 1
    WEIGHT_DOMAIN_RANGE = 0.25
    DIM_WORDS = 100
    DIM_DOMAIN_RANGE = 100

    filterWords = False
    filterDuplicates = True
    filepathOPD = CST.PATH.OPD
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
            opData.getNameSplit(True, True, CST.WORDS.getWordsSearched() if filterWords else [])
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
    docOp = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(opNamesSplitted + CST.LINK_WORDS_CLUSTERS)]
    docEntities = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(entities)]

    model = gs.models.Doc2Vec(docOp, vector_size=DIM_WORDS)
    modelEnt = gs.models.Doc2Vec(docEntities, vector_size=DIM_DOMAIN_RANGE)

    opVecs = np.zeros((len(opNamesSplitted), DIM_WORDS + DIM_DOMAIN_RANGE))
    for i, splitted in enumerate(opNamesSplitted):
        if (i+1) % 1000 == 0:
            prt("Inferring vectors... (%d/%d): " % (i+1, len(opNamesSplitted)))
        # Note: Default epoch is 5.
        vec = model.infer_vector(splitted, epochs=10) * WEIGHT_WORDS
        vecEnt = modelEnt.infer_vector(entities[i], epochs=10) * WEIGHT_DOMAIN_RANGE
        vec2 = np.concatenate((vec, vecEnt))
        vec3 = np.concatenate((vec2, properties[i]))
        opVecs[i] = vec2

    prt("Compute %s..." % "KMeans")
    kmeans = KMeans(n_clusters=nbClusters)
    preds = kmeans.fit_predict(opVecs)

    clusters = get_clusters(nbClusters, preds, opNamesSplitted)

    #docLW = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(Csts.LINK_WORDS_CLUSTERS)]
    #modelLW = gs.models.Doc2Vec(docOp, vector_size=200)
    allVecsClusters = []
    for cluster in CST.LINK_WORDS_CLUSTERS:
        vecsCluster = []
        for word in cluster:
            nameSplit = str_list_lower(split_op_name(word))
            vec = model.infer_vector(nameSplit, epochs=10)
            vecsCluster.append(vec)
        allVecsClusters.append(vecsCluster)

    filepathClassif = "results/gensim/test_classif.txt"
    fTest = create_result_file(filepathClassif, opd.getSrcpath(), opd.getVersion())
    i = 0
    for splitted in opNamesSplitted:
        vec = model.infer_vector(str_list_lower(splitted), epochs=10)

        minSqDist = 9999999
        maxSqDist = -1
        j = 0
        clusterIndex = -1
        wordIndex = -1
        for vecsCluster in allVecsClusters:
            k = 0
            for vecCluster in vecsCluster:
                sqDist = dist(vec, vecCluster)
                if sqDist < minSqDist:
                    minSqDist = sqDist
                    clusterIndex = j
                    wordIndex = k
                if sqDist > maxSqDist:
                    maxSqDist = sqDist
                k += 1
            j += 1

        distProportion = to_percent(minSqDist, maxSqDist)
        if distProportion < 0.1:
            fTest.write("Name %-40s => %-40s (word=%s, min=%f)\n" % (
                opd.getData()[i].getOpName(), CST.LINK_WORDS_CLUSTERS_NAMES[clusterIndex],
                CST.LINK_WORDS_CLUSTERS[clusterIndex][wordIndex], distProportion))
        i += 1
    prt("Compute of classification done. Results in \"%s\"" % filepathClassif)
    fTest.close()

    centers = get_clusters_centers(opVecs, DIM_WORDS + DIM_DOMAIN_RANGE)
    centersNames = get_clusters_centers_names(clusters, centers, opVecs)

    clustersLens = []
    i = 1
    for cluster in clusters:
        clustersLens.append([i] * len(cluster))
        i += 1

    prt("Compute done. Saving clusters in \"%s\"." % filepathClusters)
    save_clusters(filepathClusters, filterWords, filterDuplicates, opd, centersNames, clusters)
    prt("Labels = ", centersNames)



if __name__ == "__main__":
    # test_load()
    # test_gen_model()
    # test_graphviz()
    tests_gs_ft()
