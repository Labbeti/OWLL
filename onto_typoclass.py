from csv_fcts import *

TYPO_WORDS = ["characterize", "identifies", "defined", "depicted", "qualifies", "delineated", "specific",
              "belongs", "includes", "gathered", "collects", "isComposedOf", "contains", "assimilates", "do",
              "realizes", "assume", "accomplishes", "executes", "proceeds", "manages", "ensures", "order",
              "trigger", "causes", "helps", "contributesTo", "collaboratesIn", "participatesIn", "encourages",
              "support", "takesPartIn", "stimulates", "promotes", "increases", "amplifies", "facilitates",
              "uses", "makeUseOf", "employs", "callsUpon", "aimsTo", "isLookingFor", "continues", "tendsto",
              "research", "wishes", "dependsOn", "requires", "influence", "determines", "allows", "related",
              "necessary", "about", "transforms", "modified", "converts", "trafficking", "affects",
              "takeCareOf", "concerns", "product", "cause", "causes", "generate", "resultsIn", "created",
              "develops", "deal", "provides"]


def class_with_typo_words():
    filepath_fasttext = "data/wiki-news-300d-1M.vec"
    filepath_dbpedia = "data/ontologies/dbpedia_2016-10.owl"
    limit = 10000

    data, n, d = load_vectors(filepath_fasttext, limit)
    # TODO