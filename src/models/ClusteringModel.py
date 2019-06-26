import numpy as np
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from sklearn.cluster import AgglomerativeClustering, Birch, KMeans, MiniBatchKMeans, SpectralClustering, \
    AffinityPropagation, MeanShift
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors
from src.CST import CST
from src.controllers.ISaveController import ISaveController
from src.models.ClusteringParameters import ClusteringParameters
from src.models.ClusteringSubject import ClusteringSubject
from src.ontology.OPD import OPD
from src.util import dbg, str_list_lower, is_unreadable, sq_dist, split_op_name
from src.WordDictionary import WordDictionary

HAS_RANDOM_STATE = ["GaussianMixture", "KMeans", "MiniBatchKMeans", "SpectralClustering"]
DEFAULT_RANDOM_STATE = 2019
LIMIT = 10000
EPOCHS = 5


class ProgressManager:
    def __init__(self, subject: ClusteringSubject):
        self.subject = subject
        self.currentProgress = 0
        self.maxProgress = 1

    def getProgressProportion(self) -> float:
        return self.currentProgress / self.maxProgress

    def incrProgress(self, step: str):
        self.currentProgress += 1
        self.subject.notifyProgress(step, self.getProgressProportion())

    def reset(self, maxProgress: int):
        self.currentProgress = 0
        self.maxProgress = maxProgress


class VecsCreator:
    def __init__(self, progressManager: ProgressManager):
        self.progressManager = progressManager

    def extractVecsAndNames(self, opd: OPD, filterENWords: bool, enWordsDict: WordDictionary) \
            -> (list, list, list, list, list):
        vecsFctWords = []
        vecsMathProps = []
        contentWords = []
        opNames = []
        opWithDr = []
        domainsAndRanges = []

        for i, opData in enumerate(opd.getData()):
            if i > LIMIT:
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
            vecFctWords = [float(len([word for word in nameSplit if word == fctWord]))
                           for fctWord in CST.WORDS.getWordsSearched()]

            # Update main lists
            if len(nameSplit) > 0:
                for domain in domains:
                    for range_ in ranges:
                        vecsFctWords.append(vecFctWords)
                        vecsMathProps.append(vecMathProps)
                        contentWords.append(nameCw)
                        opNames.append(opData.getOpName())
                        opWithDr.append([domain] + nameSplit + [range_])
                        domainsAndRanges.append([domain, range_])

            if self.progressManager is not None:
                self.progressManager.incrProgress("Step %d/%d: Compute OPD data..." % (2, 4))

        return vecsFctWords, vecsMathProps, contentWords, opNames, opWithDr, domainsAndRanges

    def inferVecs(self, text: list, dim: int) -> (np.array, Doc2Vec):
        docs = [TaggedDocument(doc, [i]) for i, doc in enumerate(text)]
        doc2Vec = Doc2Vec(docs, vector_size=dim)
        matrix = np.zeros((len(text), dim))

        for i, words in enumerate(text):
            matrix[i] = doc2Vec.infer_vector(words, epochs=EPOCHS)
            self.progressManager.incrProgress("Step %d/%d: Infer vectors..." % (3, 4))
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
                centersNames[i] = "[EMPTY_CLUSTER_INDEX_%d]" % i
        return centersNames, centersVecs


class ClusteringModel(ClusteringSubject):
    def __init__(self, opdPath: str, wordDictPath: str):
        ClusteringSubject.__init__(self)
        self.opdPath = opdPath
        self.wordDictPath = wordDictPath

        self.params = ClusteringParameters()
        self.opd = OPD()
        self.enWordsDict = WordDictionary(wordDictPath)
        self.clustersNames = []
        self.centersNames = []
        self.progressManager = ProgressManager(self)
        self.saveController = None
        self.d2vCw = None
        self.d2vDr = None
        self.d2vWordsWithDr = None
        self.mainMatrix = None
        self.preds = None
        self.opNames = None

    def clustering(self, params: ClusteringParameters):
        self.params = params
        self.notifyClusteringBegan()

        # Step 1 : Load OPD
        self.notifyProgress("Step %d/%d: Reading OPD..." % (1, 4), 0)
        self.opd.loadFromFile(self.opdPath)
        self.notifyProgress("Step %d/%d: Reading OPD done." % (1, 4), 1)

        vecsCreator = VecsCreator(self.progressManager)

        # Step 2 : Read the OPD data to extract vectors and list of names
        self.progressManager.reset(self.opd.getSize())
        vecsFctWords, vecsMathProps, splittedCW, self.opNames, splittedOpsWithDR, domainsAndRanges = \
            vecsCreator.extractVecsAndNames(self.opd, self.params["FilterENWords"], self.enWordsDict)

        # Step 3 : Infer vectors with Gensim
        self.progressManager.reset(len(splittedCW) * 3)
        vecsCw, self.d2vCw = vecsCreator.inferVecs(splittedCW, self.params["DimCW"])
        vecsDr, self.d2vDr = vecsCreator.inferVecs(domainsAndRanges, self.params["DimDR"])
        vecsWordsWithDr, self.d2vWordsWithDr = vecsCreator.inferVecs(splittedOpsWithDR, self.params["DimOPWithDR"])

        self.mainMatrix, mainDim = \
            self.concatenateAll(vecsFctWords, vecsMathProps, vecsCw, vecsWordsWithDr, vecsDr)

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

    def concatenateAll(self, fctWordsVecs, mathPropsVecs, splittedCWVecs, splittedWithDRVecs, drVecs, axis=1) \
            -> (np.array, int):
        fctWordsVecs = np.array(fctWordsVecs) * self.params["WeightFctWords"]
        mathPropsVecs = np.array(mathPropsVecs) * self.params["WeightMathProps"]
        splittedWithDRVecs = np.array(splittedWithDRVecs) * self.params["WeightCW"]
        splittedCWVecs = np.array(splittedCWVecs) * self.params["WeightOPWithDR"]
        drVecs = np.array(drVecs) * self.params["WeightDR"]

        dbg("fctWordsVecs = ", fctWordsVecs.shape)
        dbg("mathPropsVecs = ", mathPropsVecs.shape)
        dbg("splittedWithDRVecs = ", splittedWithDRVecs.shape)
        dbg("splittedCWVecs = ", splittedCWVecs.shape)
        dbg("drVecs = ", drVecs.shape)

        tmp = np.concatenate((fctWordsVecs, mathPropsVecs), axis=axis)
        tmp2 = np.concatenate((tmp, splittedWithDRVecs), axis=axis)
        tmp3 = np.concatenate((tmp2, splittedCWVecs), axis=axis)
        mainVecs = np.concatenate((tmp3, drVecs), axis=axis)
        dbg("mainVecs = ", mainVecs.shape)
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

        deterministic = self.params["Deterministic"]
        if deterministic and name in HAS_RANDOM_STATE:
            clustAlgo.random_state = DEFAULT_RANDOM_STATE
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

        vecCw = self.d2vCw.infer_vector(nameCw, epochs=EPOCHS)
        vecWordsWithDr = self.d2vWordsWithDr.infer_vector(splittedWithDR, epochs=EPOCHS)
        vecDr = self.d2vDr.infer_vector(domainAndRange, epochs=EPOCHS)

        mainVec, _ = self.concatenateAll(vecFctWords, vecMathProps, vecCw, vecWordsWithDr, vecDr, axis=0)

        # Search the associated cluster
        knn = NearestNeighbors(n_neighbors=10)
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
