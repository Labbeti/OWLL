import numpy as np


class Config:
    VERBOSE_MODE = True

    CONSOLE_PREFIX = "§ "
    RDFLIB_FORMATS = ['xml', 'n3', 'nt', 'trix', 'rdfa']
    CONNECT_WORDS = ["a", "about", "as", "at", "by", "for", "has", "in", "is", "of", "on", "so", "the", "to", "with"]

    COLORS = np.array(['#377eb8', '#ff7f00', '#4daf4a', '#f781bf', '#a65628',
                       '#984ea3', '#999999', '#e41a1c', '#dede00', '#000000'])

    LINK_DOMAIN = "http://www.w3.org/2000/01/rdf-schema#domain"
    LINK_OBJECT_PROPERTY = "http://www.w3.org/2002/07/owl#ObjectProperty"
    LINK_RANGE = "http://www.w3.org/2000/01/rdf-schema#range"
    LINK_RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    LINK_THING = "http://www.w3.org/2002/07/owl#Thing"

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

    TYPO_WORDS_EXTENDED = ["characterize", "isSpecificTo", "identifies", "defined", "depicted", "qualifies",
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
