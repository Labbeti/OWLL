from Csts import Csts
from file_io import create_result_file

from gensim import corpora
from gensim import models
from gensim import similarities
from gensim.models import FastText
from gensim.models import TfidfModel
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.models import KeyedVectors
from gensim.models import Word2Vec
from gensim.similarities import SparseMatrixSimilarity
from gensim.test.utils import common_texts, get_tmpfile

from graphviz import Digraph

from ontology.OwlreadyOntology import OwlreadyOntology
from ontology.RdflibOntology import RdflibOntology
from owll_gensim import get_names_opd
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from time import time
from util import *

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


if __name__ == "__main__":
    # test_load()
    # test_gen_model()
    # test_graphviz()
    tests_gs_ft()
