import numpy as np


class CST:
    """
        Class with constant values for OWLL project.
    """

    VERBOSE_MODE = True
    DEBUG_MODE = False
    LOAD_DEFAULTS_FILES = True

    TERMINAL_PREFIX = "% "
    RDFLIB_FORMATS = ['xml', 'n3', 'nt', 'trix', 'rdfa']

    class PATH:
        """
            Defaults paths for OWLL.
        """

        # Dirs
        ONTOLOGIES = "data/ontologies/"
        # Data files
        FASTTEXT = "data/fasttext/wiki-news-300d-1M.vec"
        DBPEDIA = "data/ontologies/dbpedia_2016-10.owl"
        ENGLISH_WORDS = "data/infochimps/words.txt"
        # Results files
        CLUST = "results/clust/clusters.txt"
        OPD = "results/opd/opd.txt"
        CLUSTER_MODEL = "results/models/clusters_test.json"
        STATS_GLOBAL = "results/stats/global.txt"
        STATS_LISTS = "results/stats/op_lists.txt"
        STATS_CW = "results/stats/content_words.txt"
        STATS_SEARCHED_WORDS = "results/stats/searched_words_stats.txt"
        TYPO_LINK = "results/typolink/classif.txt"
        NON_EN_WORDS = "results/stats/non_en_words.txt"
        STATS_PAIRS_SW = "results/stats/pairs_sw.txt"

    class GUI:
        SLIDER_PRECISION = 100
        SLIDER_LABEL_FORMAT = "%.2f"
        BUTTON_MIN_HEIGHT = 30

    KNN_NB_NEIGHBORS = 10
    HAS_RANDOM_STATE = ["GaussianMixture", "KMeans", "MiniBatchKMeans", "SpectralClustering"]
    DEFAULT_RANDOM_STATE = 2019
    OP_CLUST_LIMIT = 100000  # Used for debug
    EPOCHS = 5
    MAX_RANDOM_CENTER_TRY = 10000

    MATH_PROPERTIES = \
        ["Asymmetric", "Functional", "InverseFunctional", "Irreflexive", "Reflexive", "Symmetric", "Transitive"]

    CLUSTERING_ALGORITHMS_NAMES = [
        "AgglomerativeClustering",
        "Birch",
        "GaussianMixture",
        "KMeans",
        "MiniBatchKMeans",
        "SpectralClustering",
        "AffinityPropagation",
        "MeanShift",
    ]

    COLORS = np.array([
        '#377eb8', '#ff7f00', '#4daf4a', '#f781bf', '#a65628', '#984ea3', '#999999', '#e41a1c', '#dede00', '#000000',
        '#222222', '#cccccc', '#cc00cc'])

    TENSES = [
        "infinitive",
        "1st singular present",
        "2nd singular present",
        "3rd singular present",
        "present plural",
        "present participle",
        "1st singular past",
        "2nd singular past",
        "3rd singular past",
        "past plural",
        "past",
        "past participle",
    ]
    # TENSES_INDEXES = {TENSES[i]: i for i in range(len(TENSES))}

    class WORDS:
        """
            Differents sets of functions words searched in OP.
        """

        # Prepositions or postpositions words. Unused: under
        ADPOSITIONS = "as at by for from in of on to until with".split()
        ARTICLES = "a an the".split()
        PARTICLES = "and but do if in let not out over so to up".split()
        PRONOUN = "he her him his i it its me my none our she some their them they this us we which you your".split()
        AUXILIARY_VERBS = \
            "be can could dare do did has have is may might must need ought shall should were will would".split()
        EXPLETIVES = "it there".split()
        COORDINATING_CONJUNCTIONS = "and but for nor or so yet".split()

        @staticmethod
        def getWordsSearched() -> list:
            return "has is of by in to".split()

    class IRI:
        """
            Internationalized Resource Identifier (IRI) for RDF and OWL entities and properties.
        """
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
        TOP_OBJECT_PROPERTY = "http://www.w3.org/2002/07/owl#topObjectProperty"

        class MATH_PROPERTIES:
            ASYMMETRIC = "http://www.w3.org/2002/07/owl#AsymmetricProperty"
            FUNCTIONAL = "http://www.w3.org/2002/07/owl#FunctionalProperty"
            INVERSE_FUNCTIONAL = "http://www.w3.org/2002/07/owl#InverseFunctionalProperty"
            IRREFLEXIVE = "http://www.w3.org/2002/07/owl#IrreflexiveProperty"
            REFLEXIVE = "http://www.w3.org/2002/07/owl#ReflexiveProperty"
            SYMMETRIC = "http://www.w3.org/2002/07/owl#SymmetricProperty"
            TRANSITIVE = "http://www.w3.org/2002/07/owl#TransitiveProperty"

    # Defaults words used by "owll_typolink.py".
    LINK_WORDS = [
        "characterize", "identifies", "defined", "depicted", "qualifies", "delineated", "specific",
        "belongs", "includes", "gathered", "collects", "isComposedOf", "contains", "assimilates", "do",
        "realizes", "assume", "accomplishes", "executes", "proceeds", "manages", "ensures", "order",
        "trigger", "causes", "helps", "contributesTo", "collaboratesIn", "participatesIn", "encourages",
        "support", "takesPartIn", "stimulates", "promotes", "increases", "amplifies", "facilitates",
        "uses", "makeUseOf", "employs", "callsUpon", "aimsTo", "isLookingFor", "continues", "tendsto",
        "research", "wishes", "dependsOn", "requires", "influence", "determines", "allows", "related",
        "necessary", "about", "transforms", "modified", "converts", "trafficking", "affects",
        "takeCareOf", "concerns", "product", "cause", "causes", "generate", "resultsIn", "created",
        "develops", "deal", "provides"]

    LINK_WORDS_EXTENDED = [
        "characterize", "isSpecificTo", "identifies", "defined", "depicted", "qualifies",
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

    LINK_WORDS_CLUSTERS_NAMES = [
        "Characterization",
        "Use of the example",
        "Classification",
        "Decomposition",
        "Sequence",
        "Order of size",
        "Main topic",
        "Topic help",
        "Instrument",
        "Goal",
        "Terms and conditions",
        "Object",
        "Result",
    ]
    LINK_WORDS_CLUSTERS = [
        # Characterization
        ["characterize", "isSpecificTo", "identifies", "defined", "depicted", "qualifies", "delineated", "specificTo",
         "belongsTo"],
        # Use of the example
        ["isA", "illustrationOf", "famous", "higlights", "testifiedTo", "isAnAspectOf", "remindsMeOf", "isAnExampleOf"],
        # Classification
        ["includes", "gathered", "collects"],
        # Decomposition
        ["isComposedOf", "contains", "assimilates"],
        # Sequence
        ["preceding", "comesBefore", "pre-existsAt", "isAPrerequisiteFor", "isPriorTo", "lead", "continuesWith",
         "isContinuedBy", "endsWith", "isAtTheOriginOf", "isReplacedBy"],
        # Order of size
        ["isSmallerThan", "isLessThan", "isWorseThan", "isExceededBy"],
        # Main topic
        ["do", "realizes", "assume", "accomplishes", "executes", "proceedsTo", "manages", "ensures", "order",
         "trigger", "causes"],
        # Topic help
        ["helpsTo", "contributesTo", "collaboratesIn", "participatesIn", "encourages", "support", "takesPartIn",
         "stimulates", "promotes", "increases", "amplifies", "facilitates"],
        # Instrument
        ["uses", "usesTheFollowing", "makeUseOf", "employs", "callsUpon", "hasAtItsDisposal"],
        # Goal
        ["aimsTo", "isLookingFor", "continues", "tendsTo", "research", "wishes"],
        # Terms and conditions
        ["dependsOn", "requires", "isSubjectTo", "isInfluencedBy", "isAFunctionOf", "isDeterminedBy", "isRelatedTo",
         "determines", "allows", "necessary"],
        # Object
        ["isAbout", "transforms", "modified", "converts", "trafficking", "affects", "takeCareOf", "concerns"],
        # Result
        ["product", "cause", "causes", "generate", "resultsIn", "created", "develops", "deal", "provides"],
    ]
