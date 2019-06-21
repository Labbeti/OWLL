import gensim as gs
import json
import numpy as np

from abc import abstractmethod
from sklearn.cluster import AgglomerativeClustering, Birch, KMeans, MiniBatchKMeans, SpectralClustering, \
    AffinityPropagation, MeanShift
from sklearn.mixture import GaussianMixture
from src.Csts import Csts
from src.models.ClusteringParameters import ClusteringParameters
from src.OPD import OPD
from src.util import dbg, str_list_lower, is_unreadable, sq_dist
from src.WordDictionary import WordDictionary


class ClusteringObserver:
    @abstractmethod
    def onClusteringEnded(self, clustersNames: list, centersNames: list):
        raise Exception("Not implemented")


class ClusteringSubject:
    def __init__(self):
        self.observers = []

    def addObs(self, obs: ClusteringObserver):
        self.observers.append(obs)

    def notifyClusteringEnded(self, clustersNames: list, centersNames: list):
        for obs in self.observers:
            obs.onClusteringEnded(clustersNames, centersNames)


class VecsCreator:
    def __init__(self):
        self.limit = 10000
        self.doc2VecModel = None

    def extractVecsAndNames(self, opd: OPD, filterENWords: bool, enWordsDict: WordDictionary) \
            -> (list, list, list, list, list):
        fctWordsVecs = []
        mathPropsVecs = []
        splittedCW = []
        splittedOps = []
        splittedOpsWithDR = []

        dbg("Step %d/%d: Compute OPD data..." % (1, 3))
        for i, opData in enumerate(opd.getData()):
            if i > self.limit:
                break
            # Maths properties values
            isAsym = float(opData.isAsymmetric())
            isFunc = float(opData.isFunctional())
            isInFu = float(opData.isInverseFunctional())
            isIrre = float(opData.isIrreflexive())
            isRefl = float(opData.isReflexive())
            isSymm = float(opData.isSymmetric())
            isTran = float(opData.isTransitive())
            mathPropVec = np.array([isAsym, isFunc, isInFu, isIrre, isRefl, isSymm, isTran], dtype=float)

            # Name values
            splitted = str_list_lower(opData.getNameSplit())
            splittedWithoutWords = str_list_lower(opData.getNameSplit(True, True, Csts.Words.getWordsSearched()))
            if filterENWords:
                splitted = enWordsDict.filterUnknownWords(splitted, False)
                splittedWithoutWords = enWordsDict.filterUnknownWords(splittedWithoutWords, False)

            # Get Domains and ranges
            domains = [domain for domain in opData.getDomainsNames() if not is_unreadable(domain)]
            ranges = [range_ for range_ in opData.getRangesNames() if not is_unreadable(range_)]
            if filterENWords:
                domains = enWordsDict.filterUnknownWords(domains, False)
                ranges = enWordsDict.filterUnknownWords(ranges, False)
            if len(domains) == 0:
                domains = ["Thing"]
            if len(ranges) == 0:
                ranges = ["Thing"]

            # Update fct words list
            fctWordVec = [float(len([word for word in splitted if word == fctWord]))
                          for fctWord in Csts.Words.getWordsSearched()]

            # Update main lists
            for domain in domains:
                for range_ in ranges:
                    fctWordsVecs.append(fctWordVec)
                    mathPropsVecs.append(mathPropVec)
                    splittedCW.append(splittedWithoutWords)
                    splittedOps.append(splitted)
                    splittedOpsWithDR.append([domain] + splitted + [range_])

        return fctWordsVecs, mathPropsVecs, splittedCW, splittedOps, splittedOpsWithDR

    def inferVecs(self, splittedCW: list, splittedOpsWithDR: list, dimModel: int) -> (np.array, np.array):
        if len(splittedCW) != len(splittedOpsWithDR):
            raise Exception("Invalid arguments")

        document = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(splittedOpsWithDR)]
        doc2VecModel = gs.models.Doc2Vec(document, vector_size=dimModel)

        splittedWithDRVecs = np.zeros((len(splittedOpsWithDR), dimModel))
        splittedCWVecs = np.zeros((len(splittedOpsWithDR), dimModel))

        dbg("Step %d/%d: Infering OP vectors... (%d)" % (2, 3, len(splittedOpsWithDR)))
        for i in range(len(splittedCW)):
            wordsWithout = splittedCW[i]
            wordsWithDR = splittedOpsWithDR[i]

            if (i + 1) % int(len(splittedOpsWithDR) / 10) == 0:
                dbg("%.1f%% done. (%d/%d)" % (
                round(100 * (i + 1) / len(splittedOpsWithDR)), i + 1, len(splittedOpsWithDR)))

            vec1 = doc2VecModel.infer_vector(wordsWithout, epochs=10)
            splittedCWVecs[i] = vec1
            vec2 = doc2VecModel.infer_vector(wordsWithDR, epochs=10)
            splittedWithDRVecs[i] = vec2
        return splittedCWVecs, splittedWithDRVecs


class ClustersManager:
    def getClusters(self, nbClusters: int, preds: list, opNamesSplitted: list, mainMatrix: np.array) -> (list, list):
        clustersNames = [[] for _ in range(nbClusters)]
        clustersVecs = [[] for _ in range(nbClusters)]
        for i, pred in enumerate(preds):
            opNameUsed = "".join([word.title() for word in opNamesSplitted[i]])
            clustersNames[pred].append(opNameUsed)
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
    def __init__(self):
        super().__init__()
        self.params = ClusteringParameters()
        self.filepath = ""

        self.opd = OPD()
        self.enWordsDict = None  # TODO: WordDictionary(Csts.Paths.ENGLISH_WORDS)
        self.clustersNames = []
        self.centersNames = []

    def clustering(self, params: ClusteringParameters):
        self.params = params
        self.opd.loadFromFile("results/opd/opd.txt")

        vecsCreator = VecsCreator()
        fctWordsVecs, mathPropsVecs, splittedCW, splittedOps, splittedOpsWithDR = \
            vecsCreator.extractVecsAndNames(self.opd, self.params["FilterENWords"], self.enWordsDict)
        splittedCWVecs, splittedWithDRVecs = \
            vecsCreator.inferVecs(splittedCW, splittedOpsWithDR, self.params["DimD2VModel"])
        mainMatrix, mainDim = self.concatenateAll(fctWordsVecs, mathPropsVecs, splittedCWVecs, splittedWithDRVecs)

        dbg("Step %d/%d: Cluterize vectors with %s and %d clusters..." % (
            3, 3, self.params["Algorithm"], self.params["NbClusters"]))
        clustAlgo = self.createClustAlgo()
        preds = clustAlgo.fit_predict(mainMatrix)

        manager = ClustersManager()
        self.clustersNames, clustersVecs = manager.getClusters(clustAlgo.n_clusters, preds, splittedOps, mainMatrix)
        self.centersNames, centersVecs = manager.getClustersCenters(self.clustersNames, clustersVecs, mainDim)
        self.notifyClusteringEnded(self.clustersNames, self.centersNames)

    def concatenateAll(self, fctWordsVecs, mathPropsVecs, splittedCWVecs, splittedWithDRVecs, axis=1) \
            -> (np.array, int):
        fctWordsVecs = np.array(fctWordsVecs) * self.params["WeightFctWords"]
        mathPropsVecs = np.array(mathPropsVecs) * self.params["WeightMathProps"]
        splittedWithDRVecs = np.array(splittedWithDRVecs) * self.params["WeightContentWords"]
        splittedCWVecs = np.array(splittedCWVecs) * self.params["WeightWordsWithDR"]

        dbg("fctWordsVecs = ", fctWordsVecs.shape)
        dbg("mathPropsVecs = ", mathPropsVecs.shape)
        dbg("splittedWithDRVecs = ", splittedWithDRVecs.shape)
        dbg("splittedCWVecs = ", splittedCWVecs.shape)

        tmp = np.concatenate((fctWordsVecs, mathPropsVecs), axis=axis)
        tmp2 = np.concatenate((tmp, splittedWithDRVecs), axis=axis)
        mainVecs = np.concatenate((tmp2, splittedCWVecs), axis=axis)
        dbg("mainVecs = ", mainVecs.shape)
        mainDim = mainVecs.shape[axis]
        return mainVecs, mainDim

    def createClustAlgo(self):
        name = self.params["Algorithm"]
        nbClusters = self.params["NbClusters"]
        if name == "AgglomerativeClustering":
            return AgglomerativeClustering(n_clusters=nbClusters)
        elif name == "Birch":
            return Birch(n_clusters=nbClusters)
        elif name == "GaussianMixture":
            return GaussianMixture(n_components=nbClusters)
        elif name == "KMeans":
            return KMeans(n_clusters=nbClusters)
        elif name == "MiniBatchKMeans":
            return MiniBatchKMeans(n_clusters=nbClusters)
        elif name == "SpectralClustering":
            return SpectralClustering(n_clusters=nbClusters)
        elif name == "AffinityPropagation":
            return AffinityPropagation()
        elif name == "MeanShift":
            return MeanShift()
        else:
            raise Exception("Unknown algorithm %s" % name)

    def loadFromFile(self, filepath: str) -> bool:
        dbg("Load model = ", filepath)
        self.filepath = filepath

        try:
            fIn = open(filepath, "r", encoding="utf-8")
        except IOError:
            # TODO : print error to user
            return False

        data = json.load(fIn)
        self.params = data["params"]
        # TODO : read self.clustersNames, self.centersNames

        fIn.close()
        self.notifyClusteringEnded(self.clustersNames, self.centersNames)
        return True

    def saveInFile(self, filepath: str):
        dbg("Save model = ", filepath)
        data = dict()
        data["params"] = self.params
        fOut = open(filepath, "w", encoding="utf-8")
        json.dump(data, fOut, ensure_ascii=False, indent=4)
        fOut.close()

    def getFilepath(self):
        return self.filepath

    def getParams(self) -> ClusteringParameters:
        return self.params
