import numpy as np
from random import randint
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from gensim.corpora.dictionary import Dictionary
from sklearn.cluster import AgglomerativeClustering, Birch, KMeans, MiniBatchKMeans, SpectralClustering, \
    AffinityPropagation, MeanShift
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors
from src.CST import CST
from src.controllers.ISaveController import ISaveController
from src.models.ClusteringParameters import ClusteringParameters
from src.models.ClusteringSubject import ClusteringSubject
from src.models.ontology import OPD
from src.ProgressSubject import ProgressSubject
from src.util import dbg, str_list_lower, is_unreadable, sq_dist, split_op_name
from src.WordDictionary import WordDictionary


class VecsCreator:
    def __init__(self, progressSubject: ProgressSubject):
        self.progressSubject = progressSubject

    def createFctWordVec(self, nameSplit: list) -> list:
        if len(nameSplit) == 0:
            return [0. for _ in range(len(CST.WORDS.getWordsSearched()) * 3 + 3)]

        prefixVec = [1. if nameSplit[0] == fctWord else 0. for fctWord in CST.WORDS.getWordsSearched()]
        suffixVec = [1. if nameSplit[-1] == fctWord else 0. for fctWord in CST.WORDS.getWordsSearched()]
        infixVec = [1. if fctWord in nameSplit[1:len(nameSplit) - 1] else 0. for fctWord in
                    CST.WORDS.getWordsSearched()]

        hasPrefix = 1. if sum(prefixVec) > 0 else 0.
        hasSuffix = 1. if sum(suffixVec) > 0 else 0.
        hasInfix = 1. if sum(infixVec) > 0 else 0.

        return prefixVec + suffixVec + infixVec + [hasPrefix, hasSuffix, hasInfix]

    def extractVecsAndNames(self, opd: OPD, filterENWords: bool, enWordsDict: WordDictionary) \
            -> (list, list, list, list, list):
        vecsFctWords = []
        vecsMathProps = []
        contentWords = []
        opNames = []
        opWithDr = []
        domainsAndRanges = []

        for i, opData in enumerate(opd.getData()):
            if i > CST.OP_CLUST_LIMIT:
                dbg("Limit reached for extractVecsAndNames.")
                break
            # Maths properties values
            isAsym = float(opData.isAsymmetric())
            isFunc = float(opData.isFunctional())
            isInFu = float(opData.isInverseFunctional())
            isIrre = float(opData.isIrreflexive())
            isRefl = float(opData.isReflexive())
            isSymm = float(opData.isSymmetric())
            isTran = float(opData.isTransitive())
            vecMathProps = np.array([isAsym, isFunc, isInFu, isIrre, isRefl, isSymm, isTran], dtype=float)

            # Name values
            nameSplit = str_list_lower(opData.getNameSplit())
            nameCw = str_list_lower(opData.getNameSplit(True, True, CST.WORDS.getWordsSearched()))
            if filterENWords:
                nameSplit = enWordsDict.filterUnknownWords(nameSplit, False)
                nameCw = enWordsDict.filterUnknownWords(nameCw, False)

            # Get Domains and ranges
            domains = [domain for domain in opData.getDomainsNames() if not is_unreadable(domain)]
            ranges = [range_ for range_ in opData.getRangesNames() if not is_unreadable(range_)]
            if len(domains) == 0:
                domains = ["Thing"]
            if len(ranges) == 0:
                ranges = ["Thing"]
            if filterENWords:
                domains = enWordsDict.filterUnknownWords(domains, False)
                ranges = enWordsDict.filterUnknownWords(ranges, False)

            # Update fct words list
            vecFctWords = self.createFctWordVec(nameSplit)

            # Update main lists
            if len(nameSplit) > 0:
                for domain in domains:
                    for range_ in ranges:
                        vecsFctWords.append(vecFctWords)
                        vecsMathProps.append(vecMathProps)
                        contentWords.append(nameCw)
                        opNames.append(opData.getName())
                        opWithDr.append([domain] + nameSplit + [range_])
                        domainsAndRanges.append([domain, range_])

            if self.progressSubject is not None:
                self.progressSubject.incrProgress("Step %d/%d: Compute OPD data..." % (2, 4))

        return vecsFctWords, vecsMathProps, contentWords, opNames, opWithDr, domainsAndRanges

    def inferVecs(self, text: list, dim: int) -> (np.array, Doc2Vec):
        docs = [TaggedDocument(doc, [i]) for i, doc in enumerate(text)]
        doc2Vec = Doc2Vec(docs, vector_size=dim)
        matrix = np.zeros((len(text), dim))

        for i, words in enumerate(text):
            matrix[i] = doc2Vec.infer_vector(words, epochs=CST.EPOCHS)
            if self.progressSubject is not None:
                self.progressSubject.incrProgress("Step %d/%d: Infer vectors..." % (3, 4))
        return matrix, doc2Vec


class ClustersManager:
    def getClusters(self, nbClusters: int, preds: list, opNames: list, mainMatrix: np.array) -> (list, list):
        clustersNames = [[] for _ in range(nbClusters)]
        clustersVecs = [[] for _ in range(nbClusters)]
        for i, (pred, opName) in enumerate(zip(preds, opNames)):
            clustersNames[pred].append(opName)
            clustersVecs[pred].append(mainMatrix[i])
        return clustersNames, clustersVecs

    def getClustersCenters(self, clustersNames: list, clustersVecs: list, dim: int) -> (list, list):
        """
            Return a list of string names of clusters centers.
            :param clustersNames:
            :param clustersVecs:
            :param dim:
            :return:
        """
        # Compute center of each cluster
        centersVecs = [np.zeros(dim, dtype=float) for _ in range(len(clustersVecs))]
        for i, cluster in enumerate(clustersVecs):
            for vec in cluster:
                centersVecs[i] += vec
            if len(cluster) > 0:
                centersVecs[i] /= len(cluster)

        # Get the nearest vec for each cluster center
        centersNames = ["" for _ in range(len(clustersNames))]
        for i, (center, clusterVecs) in enumerate(zip(centersVecs, clustersVecs)):
            minSqDist = 9999999
            jMin = -1

            if len(clusterVecs) > 0:
                for j, vec in enumerate(clusterVecs):
                    sqDist = sq_dist(vec, center)
                    if sqDist < minSqDist:
                        minSqDist = sqDist
                        jMin = j
                centersNames[i] = clustersNames[i][jMin]
            else:
                centersNames[i] = "[EMPTY_CLUSTER_%d]" % i
        return centersNames, centersVecs


class ClusteringModel(ClusteringSubject, ProgressSubject):
    def __init__(self, opd: OPD, wordDictPath: str):
        ClusteringSubject.__init__(self)
        ProgressSubject.__init__(self)
        self.wordDictPath = wordDictPath

        self.params = ClusteringParameters()
        self.opd = opd
        self.enWordsDict = WordDictionary(wordDictPath)
        self.clustersNames = []
        self.centersNames = []
        self.saveController = None
        self.d2vCw = None
        self.d2vDr = None
        self.d2vWordsWithDr = None
        self.mainMatrix = None
        self.preds = None
        self.opNames = None

    def clustering(self, params: ClusteringParameters):
        """
            Main function for apply clusterisation on OPs found in OPD.
            :param params: Parameters of the clusterisation.
        """
        self.params = params
        self.notifyClusteringBegan()

        vecsCreator = VecsCreator(self)

        # Step 2 : Read the OPD data to extract vectors and list of names
        self.resetProgress(self.opd.getSize())
        vecsFctWords, vecsMathProps, splittedCW, self.opNames, splittedOpsWithDR, domainsAndRanges = \
            vecsCreator.extractVecsAndNames(self.opd, self.params["FilterENWords"], self.enWordsDict)

        # Check if vocabulary is enough for inferring vector
        vocabulary = Dictionary(splittedCW)
        if len(vocabulary) < self.params["NbClusters"]:
            self.notifyError(
                "Cannot infer vectors: Vocabulary of content words is smaller than number of clusters (%d < %d). "
                "Maybe add more ontologies to provide more object properties." % (len(vocabulary),
                                                                                  self.params["NbClusters"]))
            return

        # Step 3 : Infer vectors with Gensim
        self.resetProgress(len(splittedCW) * 3)
        vecsCw, self.d2vCw = vecsCreator.inferVecs(splittedCW, self.params["DimCW"])
        vecsDr, self.d2vDr = vecsCreator.inferVecs(domainsAndRanges, self.params["DimDR"])
        vecsWordsWithDr, self.d2vWordsWithDr = vecsCreator.inferVecs(splittedOpsWithDR, self.params["DimOPWithDR"])

        vecsList = [vecsFctWords, vecsMathProps, vecsCw, vecsWordsWithDr, vecsDr]
        vecsList = self.applyWeights(vecsList)
        self.mainMatrix, mainDim = self.concatenateAll(vecsList)

        # Step 4 : Clusterisation
        self.notifyProgress("Step %d/%d: Compute clusterisation..." % (4, 4), 0)
        clustAlgo = self.createClustAlgo()
        self.preds = clustAlgo.fit_predict(self.mainMatrix)
        self.notifyProgress("Step %d/%d: Compute clusterisation done." % (4, 4), 1)

        manager = ClustersManager()
        self.clustersNames, clustersVecs = manager.getClusters(
            clustAlgo.n_clusters, self.preds, self.opNames, self.mainMatrix)
        self.centersNames, centersVecs = manager.getClustersCenters(self.clustersNames, clustersVecs, mainDim)
        self.notifyClusteringEnded()

    def applyWeights(self, vecsList: list) -> list:
        weightsNamesList = ["WeightFctWords", "WeightMathProps", "WeightCW", "WeightOPWithDR", "WeightDR"]
        if len(vecsList) != len(weightsNamesList):
            raise Exception("Fatal error: possible missing of 1 weight for vectors")
        for i, vecs in enumerate(vecsList):
            if len(vecsList[i - 1]) != len(vecs):
                raise Exception("Fatal error: Vecs does have the same number of elements.")
        weightsValsList = [self.params[name] for name in weightsNamesList]
        return [np.array(vecs) * weight for vecs, weight in zip(vecsList, weightsValsList)]

    def concatenateAll(self, vecsList: list, axis: int = 1) -> (np.array, int):
        mainVecs = vecsList[0]
        for i in range(1, len(vecsList)):
            vecs = vecsList[i]
            mainVecs = np.concatenate((mainVecs, vecs), axis=axis)
        mainDim = mainVecs.shape[axis]
        return mainVecs, mainDim

    def createClustAlgo(self):
        name = self.params["Algorithm"]
        nbClusters = self.params["NbClusters"]

        if name == "AgglomerativeClustering":
            clustAlgo = AgglomerativeClustering(n_clusters=nbClusters)
        elif name == "Birch":
            clustAlgo = Birch(n_clusters=nbClusters)
        elif name == "GaussianMixture":
            clustAlgo = GaussianMixture(n_components=nbClusters)
        elif name == "KMeans":
            clustAlgo = KMeans(n_clusters=nbClusters)
        elif name == "MiniBatchKMeans":
            clustAlgo = MiniBatchKMeans(n_clusters=nbClusters)
        elif name == "SpectralClustering":
            clustAlgo = SpectralClustering(n_clusters=nbClusters)
        elif name == "AffinityPropagation":
            clustAlgo = AffinityPropagation()
        elif name == "MeanShift":
            clustAlgo = MeanShift()
        else:
            raise Exception("Unknown algorithm %s" % name)

        if name in CST.HAS_RANDOM_STATE:
            deterministic = self.params["Deterministic"]
            if deterministic:
                clustAlgo.random_state = CST.DEFAULT_RANDOM_STATE
            else:
                centers = []
                nbTry = 0
                while len(centers) < nbClusters:
                    if nbTry >= CST.MAX_RANDOM_CENTER_TRY:
                        raise Exception("Cannot select distinct centers for algorithm %s. Maybe not enough data for %d "
                                        "clusters." % (name, nbClusters))
                    rd = randint(0, len(self.mainMatrix) - 1)
                    vec = list(self.mainMatrix[rd])
                    if vec not in centers:
                        centers.append(vec)
                    nbTry += 1
                clustAlgo.init = np.array(centers)
                clustAlgo.n_init = 1
        return clustAlgo

    def submitOp(self, opName: str, domain: str, range_: str, mathProps: dict):
        dbg("submitOp = ", opName, domain, range_, mathProps.values())
        # Prepare name lists
        domain = domain.lower()
        range_ = range_.lower()

        nameSplit = str_list_lower(split_op_name(opName))
        nameCw = [word for word in nameSplit
                  if word not in CST.WORDS.getWordsSearched()
                  and word != domain
                  and word != range_]
        domainAndRange = [domain, range_]
        splittedWithDR = [domain] + nameSplit + [range_]

        # Get vectors and concatenate
        vecFctWords = [float(len([word for word in nameSplit if word == fctWord]))
                       for fctWord in CST.WORDS.getWordsSearched()]
        vecMathProps = np.array(list(mathProps.values()), dtype=float)

        vecCw = self.d2vCw.infer_vector(nameCw, epochs=CST.EPOCHS)
        vecWordsWithDr = self.d2vWordsWithDr.infer_vector(splittedWithDR, epochs=CST.EPOCHS)
        vecDr = self.d2vDr.infer_vector(domainAndRange, epochs=CST.EPOCHS)

        vecsList = [vecFctWords, vecMathProps, vecCw, vecWordsWithDr, vecDr]
        vecsList = self.applyWeights(vecsList)
        mainVec, _ = self.concatenateAll(vecsList, axis=0)

        # Search the associated cluster
        knn = NearestNeighbors(n_neighbors=CST.KNN_NB_NEIGHBORS)
        knn.fit(self.mainMatrix)
        dist, ind = knn.kneighbors([mainVec])

        ind = ind[0][0]
        if ind != -1:
            pred = self.preds[ind]
            centerName = self.centersNames[pred]
            nearest = self.opNames[ind]
            self.notifySubmitResult(centerName, nearest)
        else:
            raise Exception("Fatal error: OP matrix is probably empty")

    def getParams(self) -> ClusteringParameters:
        return self.params

    def getClusters(self) -> list:
        return self.clustersNames

    def getCenters(self) -> list:
        return self.centersNames

    def setParams(self, params: ClusteringParameters):
        self.params = params

    def setClustersNames(self, clustersNames: list):
        self.clustersNames = clustersNames

    def setCentersNames(self, centersNames: list):
        self.centersNames = centersNames

    def setSaveController(self, saveController: ISaveController):
        self.saveController = saveController
