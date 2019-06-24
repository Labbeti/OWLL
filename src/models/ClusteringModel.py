import gensim as gs
import json
import numpy as np

from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from PyQt5.QtWidgets import QMessageBox
from sklearn.cluster import AgglomerativeClustering, Birch, KMeans, MiniBatchKMeans, SpectralClustering, \
    AffinityPropagation, MeanShift
from sklearn.mixture import GaussianMixture
from src.Csts import Csts
from src.models.ClusteringParameters import ClusteringParameters
from src.models.ClusteringSubject import ClusteringSubject
from src.models.ClusteringProgressSubject import ClusteringProgressSubject
from src.OPD import OPD
from src.util import dbg, str_list_lower, is_unreadable, sq_dist
from src.WordDictionary import WordDictionary
from .. import PROJECT_VERSION

HAS_RANDOM_STATE = ["GaussianMixture", "KMeans", "MiniBatchKMeans", "SpectralClustering"]
DEFAULT_RANDOM_STATE = 2019


class VecsCreator:
    def __init__(self):
        self.limit = 10000
        self.epoch = 5

    def extractVecsAndNames(self, opd: OPD, filterENWords: bool, enWordsDict: WordDictionary) \
            -> (list, list, list, list, list):
        vecsFctWords = []
        vecsMathProps = []
        contentWords = []
        objectsProperties = []
        opWithDr = []
        domainsAndRanges = []

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
            nameSplit = str_list_lower(opData.getNameSplit())
            nameCw = str_list_lower(opData.getNameSplit(True, True, Csts.Words.getWordsSearched()))
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
            fctWordVec = [float(len([word for word in nameSplit if word == fctWord]))
                          for fctWord in Csts.Words.getWordsSearched()]

            # Update main lists
            for domain in domains:
                for range_ in ranges:
                    vecsFctWords.append(fctWordVec)
                    vecsMathProps.append(mathPropVec)
                    contentWords.append(nameCw)
                    objectsProperties.append(nameSplit)
                    opWithDr.append([domain] + nameSplit + [range_])
                    domainsAndRanges.append([domain, range_])

        return vecsFctWords, vecsMathProps, contentWords, objectsProperties, opWithDr, domainsAndRanges

    def inferVecs(self, text: list, dim: int) -> np.array:
        docs = [TaggedDocument(doc, [i]) for i, doc in enumerate(text)]
        doc2Vec = Doc2Vec(docs, vector_size=dim)
        matrix = np.zeros((len(text), dim))

        for i, words in enumerate(text):
            matrix[i] = doc2Vec.infer_vector(words, epochs=self.epoch)
        return matrix


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


class ClusteringModel(ClusteringSubject, ClusteringProgressSubject):
    def __init__(self, wordDictPath: str):
        ClusteringSubject.__init__(self)
        ClusteringProgressSubject.__init__(self)
        self.params = ClusteringParameters()
        self.filepath = ""

        self.opd = OPD()
        self.enWordsDict = WordDictionary(wordDictPath)
        self.clustersNames = []
        self.centersNames = []

    def clustering(self, params: ClusteringParameters):
        self.params = params
        self.notifyProgress("Compute OPD data...", 0)
        self.opd.loadFromFile("results/opd/opd.txt")

        vecsCreator = VecsCreator()

        # Read the OPD data to extract vectors and list of names
        dbg("Step %d/%d: Compute OPD data..." % (1, 3))
        vecsFctWords, vecsMathProps, splittedCW, splittedOps, splittedOpsWithDR, domainsAndRanges = \
            vecsCreator.extractVecsAndNames(self.opd, self.params["FilterENWords"], self.enWordsDict)

        # Infer some vectors with Gensim and list of names
        dbg("Step %d/%d: Infering OP vectors... (%d)" % (2, 3, len(domainsAndRanges)))
        self.notifyProgress("Infer vectors...", 33)
        vecsCw = vecsCreator.inferVecs(splittedCW, self.params["DimCW"])
        vecsDr = vecsCreator.inferVecs(domainsAndRanges, self.params["DimDR"])
        vecsWordsWithDr = vecsCreator.inferVecs(splittedOpsWithDR, self.params["DimOPWithDR"])

        mainMatrix, mainDim = \
            self.concatenateAll(vecsFctWords, vecsMathProps, vecsCw, vecsWordsWithDr, vecsDr)

        dbg("Step %d/%d: Cluterize vectors with %s and %d clusters..." % (
            3, 3, self.params["Algorithm"], self.params["NbClusters"]))
        self.notifyProgress("Create clusters with %s" % self.params["Algorithm"], 66)
        clustAlgo = self.createClustAlgo()
        preds = clustAlgo.fit_predict(mainMatrix)

        manager = ClustersManager()
        self.clustersNames, clustersVecs = manager.getClusters(clustAlgo.n_clusters, preds, splittedOps, mainMatrix)
        self.centersNames, centersVecs = manager.getClustersCenters(self.clustersNames, clustersVecs, mainDim)
        self.notifyProgress("Done", 100)
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

    def loadFromFile(self, filepath: str) -> bool:
        dbg("Load model = ", filepath)

        try:
            fIn = open(filepath, "r", encoding="utf-8")
        except IOError:
            box = QMessageBox()
            box.setIcon(QMessageBox.Warning)
            box.setText("Cannot open file \"%s\"." % filepath)
            box.setStandardButtons(QMessageBox.Ok)
            box.exec_()
            return False

        self.filepath = filepath

        try:
            data = json.load(fIn)
        except json.decoder.JSONDecodeError:
            box = QMessageBox()
            box.setIcon(QMessageBox.Warning)
            box.setText("File \"%s\" is not a valid JSON model file." % filepath)
            box.setStandardButtons(QMessageBox.Ok)
            box.exec_()
            return False

        self.params = data["params"]
        clustersData = data["clusters"]
        self.clustersNames = []
        self.centersNames = []
        for clusterData in clustersData:
            self.clustersNames.append(clusterData["names"])
            self.centersNames.append(clusterData["center"])

        fIn.close()
        self.notifyModelLoaded()
        return True

    def saveInFile(self, filepath: str):
        dbg("Save model = ", filepath)
        data = dict()
        metaData = dict()
        metaData["OwllVersion"] = PROJECT_VERSION
        data["meta"] = metaData
        data["params"] = self.params

        clustersData = []
        for i, cluster in enumerate(self.clustersNames):
            center = self.centersNames[i]
            clusterData = dict()
            clusterData["center"] = center
            clusterData["names"] = cluster
            clustersData.append(clusterData)
        data["clusters"] = clustersData

        fOut = open(filepath, "w", encoding="utf-8")
        json.dump(data, fOut, ensure_ascii=False, indent=4)
        fOut.close()

    def getFilepath(self):
        return self.filepath

    def getParams(self) -> ClusteringParameters:
        return self.params

    def getClusters(self) -> list:
        return self.clustersNames

    def getCenters(self) -> list:
        return self.centersNames
