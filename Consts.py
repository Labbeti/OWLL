import numpy as np


class Consts:
    VERBOSE_MODE = True

    TERMINAL_PREFIX = "% "
    RDFLIB_FORMATS = ['xml', 'n3', 'nt', 'trix', 'rdfa']

    class Path:
        class Dir:
            ONTOLOGIES = "data/ontologies/"

        class File:
            FASTTEXT = "data/fasttext/wiki-news-300d-1M.vec"
            DBPEDIA = "data/ontologies/dbpedia_2016-10.owl"
            ENGLISH_WORDS = "data/infochimps/words.txt"

            class Result:
                UNUSED_WORDS = "results/opd/unused_words.txt"
                OPD = "results/opd/opd.txt"
                OPD_DEBUG = "results/opd/opd_debug.txt"
                CLUST = "results/clust/clusters.txt"
                TYPO_LINK = "results/typolink/classif.txt"
                STATS_SEARCHED_WORDS = "results/stats/searched_words_stats.txt"
                STATS_ROOTS = "results/stats/roots.txt"
                STATS_LISTS = "results/stats/op_lists.txt"
                STATS_GLOBAL = "results/stats/global.txt"

    class Word:
        ADPOSITIONS = "as at by for from in of on to under until with".split()  # preposition or postposition words
        ARTICLES = "a an the".split()

        PARTICLES = "and but do if in let not out over so to up".split()
        PRONOUN = "he her him his i it its me my none our she some their them they this us we which you your".split()
        AUXILIARY_VERBS = "be can could dare do did has have is may might must need ought shall should were will would"\
            .split()
        EXPLETIVES = "it there".split()
        COORDINATING_CONJUNCTIONS = "and but for nor or so yet".split()

        @staticmethod
        def getWordsSearched() -> list:
            return ["has", "is"] + __class__.ARTICLES + __class__.ADPOSITIONS
        '''
        TODO
        CONNECT = ["a", "about", "as", "at", "by", "for", "has", "in", "is", "of", "on", "same", "the", "to", "with"]
        '''

    COLORS = np.array(['#377eb8', '#ff7f00', '#4daf4a', '#f781bf', '#a65628',
                       '#984ea3', '#999999', '#e41a1c', '#dede00', '#000000',
                       '#222222', '#cccccc', '#cc00cc'])

    class Uris:
        CLASS = "http://www.w3.org/2002/07/owl#Class"
        DOMAIN = "http://www.w3.org/2000/01/rdf-schema#domain"
        INTERSECTION_OF = "http://www.w3.org/2002/07/owl#intersectionOf"
        INVERSE_OF = "http://www.w3.org/2002/07/owl#inverseOf"
        LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
        OBJECT_PROPERTY = "http://www.w3.org/2002/07/owl#ObjectProperty"
        RANGE = "http://www.w3.org/2000/01/rdf-schema#range"
        RESTRICTION = "http://www.w3.org/2002/07/owl#Restriction"
        RDF_REST = "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest"
        RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        SUB_CLASS_OF = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        SUB_PROPERTY_OF = "http://www.w3.org/2000/01/rdf-schema#subPropertyOf"
        THING = "http://www.w3.org/2002/07/owl#Thing"

        class Properties:
            ASYMMETRIC = "http://www.w3.org/2002/07/owl#AsymmetricProperty"
            FUNCTIONAL = "http://www.w3.org/2002/07/owl#FunctionalProperty"
            INVERSE_FUNCTIONAL = "http://www.w3.org/2002/07/owl#InverseFunctionalProperty"
            IRREFLEXIVE = "http://www.w3.org/2002/07/owl#IrreflexiveProperty"
            REFLEXIVE = "http://www.w3.org/2002/07/owl#ReflexiveProperty"
            SYMMETRIC = "http://www.w3.org/2002/07/owl#SymmetricProperty"
            TRANSITIVE = "http://www.w3.org/2002/07/owl#TransitiveProperty"

    class DefaultOpdValues:
        LABEL = ""
        NB_INSTANCES = -1
        INVERSE_OF = ""
        SUBPROPERTY_OF = ""

    LINK_WORDS = ["characterize", "identifies", "defined", "depicted", "qualifies", "delineated", "specific",
                  "belongs", "includes", "gathered", "collects", "isComposedOf", "contains", "assimilates", "do",
                  "realizes", "assume", "accomplishes", "executes", "proceeds", "manages", "ensures", "order",
                  "trigger", "causes", "helps", "contributesTo", "collaboratesIn", "participatesIn", "encourages",
                  "support", "takesPartIn", "stimulates", "promotes", "increases", "amplifies", "facilitates",
                  "uses", "makeUseOf", "employs", "callsUpon", "aimsTo", "isLookingFor", "continues", "tendsto",
                  "research", "wishes", "dependsOn", "requires", "influence", "determines", "allows", "related",
                  "necessary", "about", "transforms", "modified", "converts", "trafficking", "affects",
                  "takeCareOf", "concerns", "product", "cause", "causes", "generate", "resultsIn", "created",
                  "develops", "deal", "provides"]

    LINK_WORDS_EXTENDED = ["characterize", "isSpecificTo", "identifies", "defined", "depicted", "qualifies",
                           "delineated", "specific", "belongs", "isA", "illustrationOf", "famous", "higlights",
                           "testifiedTo", "isAnAspectOf", "remindsMeOf", "isAnExampleOf", "includes", "gathered",
                           "collects", "isComposedOf", "contains", "assimilates", "preceding", "comesBefore",
                           "pre-existsAt", "isAPrerequisiteFor", "isPriorTo", "lead", "continuesWith", "isContinuedBy",
                           "endsWith", "isAtTheOriginOf", "isReplacedBy", "isTheFatherOf", "isSmallerThan",
                           "isLessThan", "isWorseThan", "isExceededBy", "do", "realizes", "assume", "accomplishes",
                           "executes", "proceeds", "manages", "ensures", "order", "trigger", "causes", "helps",
                           "contributesTo", "collaboratesIn", "participatesIn", "encourages", "support",
                           "takespartIn", "stimulates", "promotes", "increases", "amplifies", "facilitates", "uses",
                           "makeUseOf", "employs", "callsUpon", "hasAtItsDisposal", "aimsTo", "isLookingFor",
                           "continues", "tendsTo", "research", "wishes", "dependsOn", "requires", "influence",
                           "determines", "allows", "related", "necessary", "about", "transforms", "modified",
                           "converts", "trafficking", "affects", "takeCareOf", "concerns", "product", "cause",
                           "causes", "generate", "resultsIn", "created", "develops", "deal", "provides"]
