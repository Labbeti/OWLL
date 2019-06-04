from gensim import corpora
from gensim import models
from gensim import similarities
from gensim.models import KeyedVectors
from gensim.models import Word2Vec
from gensim.test.utils import common_texts, get_tmpfile
from ontology.Ontology import LoadType
from ontology.Ontology import Ontology
from owll_opd import read_opd
from util import *


def test_load():
    filepath = "data/ontologies/tabletopgames_V3.owl"
    onto = Ontology(filepath, LoadType.FORCE_OWLREADY2)
    print("Loaded = %d" % onto.isLoaded())


def test_gen_model():
    # fname = get_tmpfile("vectors.kv")  # search in "C:\\Users\\invite\\AppData\\Local\\Temp\\"

    filepath_opd = "results/stats/opd.txt"
    filepath_model = "results/gensim/word2vec.model"
    data, version, _ = read_opd(filepath_opd)

    names = []
    nb_names = 0
    for values in data:
        op_name = values["ObjectProperty"]
        words_name = split_name(op_name)
        words_name_lower = [word.lower() for word in words_name]
        names.append(words_name_lower)
        nb_names += len(words_name)

    print("OP = %d\nNames = %d" % (len(names), nb_names))
    #print(filepath_model)
    #model = Word2Vec(names, size=100, window=5, min_count=1, workers=4)
    #model.wv.save(filepath_model)
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
    #print(dictionary)

    rems = [["inside"], ["is", "inside"]]
    for rem in rems:
        names = list(filter(lambda op: op != rem, names))
        # names.remove(rem)
    ''' 
    '''

    corpus = [dictionary.doc2bow(text) for text in names]
    #print(corpus)

    tfidf = models.TfidfModel(corpus)

    quitting_w = ["quit", "exit", "QUIT", "EXIT"]
    user_in = ""
    while user_in not in quitting_w:
        #user_in = "is a part of"
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
        sims_vals = [1-sim for (_, sim) in similarities_by_op]
        indexes = np.argsort(sims_vals)

        (ind, sim) = similarities_by_op[indexes[0]]
        print("Similarité (1er) = %.2f (%d)" % (sim, ind))
        print("1er: ", names[indexes[0]])

        print("Similarité (2nd) = %.2f (%d)" % (sim, ind))
        print("2nd: ", names[indexes[1]])


if __name__ == "__main__":
    test_load()
    # test_gen_model()
