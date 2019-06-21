from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons, TextBox
from src.OPD import OPD
from src.old_scripts.PieEventHandler import PieEventHandler
from sklearn.cluster import AgglomerativeClustering, KMeans
from time import time
from src.util import *
from src.WordDictionary import WordDictionary

import gensim as gs
import json
import numpy as np
import matplotlib.pyplot as plt


def get_clusters(nbClusters: int, preds: list, opNamesSplitted: list, mainVecs: np.array) -> (list, list):
    clustersNames = [[] for _ in range(nbClusters)]
    clustersVecs = [[] for _ in range(nbClusters)]
    for i, pred in enumerate(preds):
        opNameUsed = "".join([word.title() for word in opNamesSplitted[i]])
        clustersNames[pred].append(opNameUsed)
        clustersVecs[pred].append(mainVecs[i])
    return clustersNames, clustersVecs


def get_clusters_centers(clustersNames: list, clustersVecs: list, dim: int) -> (list, list):
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


def get_total_nb_names(clusters: list) -> int:
    return sum([len(cluster) for cluster in clusters])


def save_clusters(filepathClusters: str, filterWords: bool, filterDuplicates: bool, opd: OPD, centersNames: list,
                  clusters: list):
    data = dict()
    metaData = dict()
    metaData["version"] = get_time()
    metaData["opd_filepath"] = opd.getSrcpath()
    metaData["opd_version"] = opd.getVersion()
    metaData["filterFctWords"] = filterWords
    metaData["filterDuplicates"] = filterDuplicates
    metaData["description"] = "This file contains a list of clusters created by OWLL. Proportions are in %"
    data["meta"] = metaData

    clustersDict = dict()
    clustersDict["size"] = len(clusters)
    nbValuesTotal = get_total_nb_names(clusters)
    clustersDict["nbNames"] = nbValuesTotal

    for i, cluster in enumerate(clusters):
        clusterName = "cluster_%d" % i
        clustersDict[clusterName] = {}
        clustersDict[clusterName]["proportion"] = to_percent(len(cluster), nbValuesTotal)
        clustersDict[clusterName]["size"] = len(cluster)
        clustersDict[clusterName]["center"] = centersNames[i]
        clustersDict[clusterName]["names"] = []
        for opName in cluster:
            clustersDict[clusterName]["names"].append(opName)
    data["clusters"] = clustersDict

    fOut = open(filepathClusters, "w", encoding="utf-8")
    json.dump(data, fOut, ensure_ascii=False, indent=4)
    fOut.close()


def get_fct_words_vec(splitted: list) -> list:
    return [float(len([word for word in splitted if word == fctWord])) for fctWord in Csts.Words.getWordsSearched()]


DEBUG_LIMIT = 1000


class ClustersManager:
    def __init__(self, filepathOpd: str):
        self.nbClusters = 13
        self.dimWordVec = 100
        self.weightMathProps = 0
        self.weightFctWords = 0
        self.weightContentWords = 0
        self.weightWordsWithDR = 1

        self.opd = OPD()
        self.opd.loadFromFile(filepathOpd)
        self.clustersNames = []
        self.clustersVecs = []
        self.centers = []
        self.centersNames = []
        self.numFig = 1
        self.clustAlgo = KMeans(n_clusters=self.nbClusters)
        self.algoName = "KMeans"
        self.algosNames = ["KMeans", "AgglomerativeClustering"]
        self.filterENWords = False
        self.wordDict = WordDictionary(Csts.Paths.ENGLISH_WORDS, False)
        self.model = None
        self.lastClusterFound = "[none]"
        self.currentSubmit = "IsFatherOf"
        self.currentDomain = "Person"
        self.currentRange = "Person"

        # Init graphics
        self.fig, ax = plt.subplots()
        plt.subplots_adjust(left=0.1, bottom=0.3)
        mng = plt.get_current_fig_manager()
        mng.set_window_title("OWLL")
        #mng.window.state('zoomed')

        self.pie = None
        self.sliderWeightContentWords = None
        self.sliderWeightFctWords = None
        self.sliderWeightMathProps = None
        self.sliderWeightWordsWithDR = None
        self.sliderNbClusters = None
        self.buttonClusterize = None
        self.buttonQuit = None

    def load(self, filepathClusters: str):
        self.clustersNames = []
        self.centersNames = []
        fIn = open(filepathClusters, "r", encoding="utf-8")
        data = json.load(fIn)
        for attrName, clustersData in data["clusters"].items():
            if attrName.startswith("cluster_"):
                self.clustersNames.append(clustersData["names"])
                self.centersNames.append(clustersData["center"])
        fIn.close()
        self.updateDraw()

    def __getData(self) -> (list, list, list, list, list):
        allFctWordVecs = []
        allMathPropVecs = []
        allSplitted = []
        allSplittedWithoutWords = []
        allSplitWithDR = []
        prt("Step %d/%d: Compute OPD data..." % (1, 4))
        for i, opData in enumerate(self.opd.getData()):
            if i > DEBUG_LIMIT:
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
            if self.filterENWords:
                splitted = self.wordDict.filterUnknownWords(splitted, False)
            splittedWithoutWords = str_list_lower(opData.getNameSplit(True, True, Csts.Words.getWordsSearched()))
            if self.filterENWords:
                splittedWithoutWords = self.wordDict.filterUnknownWords(splittedWithoutWords, False)

            # Get Domains and ranges
            IGNORED = []
            domains = [domain for domain in opData.getDomainsNames()
                       if domain not in IGNORED and not is_unreadable(domain)]
            ranges = [range_ for range_ in opData.getRangesNames()
                      if range_ not in IGNORED and not is_unreadable(range_)]

            if self.filterENWords:
                domains = self.wordDict.filterUnknownWords(domains, False)
            if self.filterENWords:
                ranges = self.wordDict.filterUnknownWords(ranges, False)

            if len(domains) == 0:
                domains = ["Thing"]
            if len(ranges) == 0:
                ranges = ["Thing"]

            # Update fct words list
            fctWordVec = get_fct_words_vec(splitted)

            # Update main lists
            for domain in domains:
                for range_ in ranges:
                    allMathPropVecs.append(mathPropVec)
                    allSplitted.append(splitted)
                    allSplitWithDR.append([domain] + splitted + [range_])
                    allFctWordVecs.append(fctWordVec)
                    allSplittedWithoutWords.append(splittedWithoutWords)

        return allFctWordVecs, allMathPropVecs, allSplitted, allSplittedWithoutWords, allSplitWithDR

    def __createMainVecs(self, allFctWordVecs, allMathPropVecs, allSplitted, allSplittedWithoutWords, allSplitWithDR) \
            -> (np.array, int):
        # Generate models and vectors
        document = [gs.models.doc2vec.TaggedDocument(doc, [i]) for i, doc in enumerate(allSplitWithDR)]
        self.model = gs.models.Doc2Vec(document, vector_size=self.dimWordVec)
        vecsWithDR = np.zeros((len(allSplitWithDR), self.dimWordVec))
        vecsCW = np.zeros((len(allSplitWithDR), self.dimWordVec))
        prt("Step %d/%d: Infering OP vectors... (%d)" % (2, 4, len(allSplitWithDR)))
        for i, (wordsWithDR, wordsWithout) in enumerate(zip(allSplitWithDR, allSplittedWithoutWords)):
            if (i + 1) % int(len(allSplitWithDR) / 10) == 0:
                prt("%.1f%% done. (%d/%d)" % (round(100 * (i + 1) / len(allSplitWithDR)), i + 1, len(allSplitWithDR)))
            vec1 = self.model.infer_vector(wordsWithDR, epochs=10)
            vecsWithDR[i] = vec1
            vec2 = self.model.infer_vector(wordsWithout, epochs=10)
            vecsCW[i] = vec2

        # Concatenate vecs
        return self.concatenateVectors(vecsWithDR, vecsCW, allFctWordVecs, allMathPropVecs)

    def clusterize(self, filepathClusters: str):
        allFctWordVecs, allMathPropVecs, allSplitted, allSplittedWithoutWords, allSplitWithDR = self.__getData()
        start = time()
        mainVecs, mainDim = self.__createMainVecs(
            allFctWordVecs, allMathPropVecs, allSplitted, allSplittedWithoutWords, allSplitWithDR)
        end = time()
        prt("Step %d/%d: Vectors inference done in %.2fs." % (3, 4, end - start))

        # Clusterisation
        prt("Step %d/%d: Cluterize vectors with %s and %d clusters..." % (3, 4, self.algoName, self.nbClusters))
        preds = self.clustAlgo.fit_predict(mainVecs)

        # Get clusters
        prt("Step %d/%d: Saving results..." % (4, 4))
        self.clustersNames, self.clustersVecs = get_clusters(self.nbClusters, preds, allSplitted, mainVecs)
        self.centersNames, self.centersVecs = get_clusters_centers(self.clustersNames, self.clustersVecs, mainDim)
        save_clusters(filepathClusters, False, False, self.opd, self.centersNames, self.clustersNames)
        prt("Done.")

    def concatenateVectors(self, vecsWithDR, vecsCW, vecsFctWords, vecsMathsProps, axis: int = 1) -> (np.array, int):
        vecsWithDR = np.array(vecsWithDR) * self.weightWordsWithDR
        vecsCW = np.array(vecsCW) * self.weightContentWords
        vecsFctWords = np.array(vecsFctWords) * self.weightFctWords
        vecsMathsProps = np.array(vecsMathsProps) * self.weightMathProps

        prt("DEBUG: vecsWithDR = ", vecsWithDR.shape)
        prt("DEBUG: vecsWithout = ", vecsCW.shape)
        prt("DEBUG: vecsFctWords = ", vecsFctWords.shape)
        prt("DEBUG: vecsMathsProps = ", vecsMathsProps.shape)

        tmp = np.concatenate((vecsWithDR, vecsCW), axis=axis)
        tmp2 = np.concatenate((tmp, vecsFctWords), axis=axis)
        mainVecs = np.concatenate((tmp2, vecsMathsProps), axis=axis)
        prt("DEBUG: mainVecs = ", mainVecs.shape)
        mainDim = mainVecs.shape[axis]
        return mainVecs, mainDim

    def updateDraw(self):
        plt.clf()
        nbNamesTotal = get_total_nb_names(self.clustersNames)
        sizes = [to_percent(len(cluster), nbNamesTotal) for cluster in self.clustersNames]
        self.pie = plt.pie(sizes, labels=self.centersNames, explode=[0.2 for _ in range(len(self.clustersNames))],
                           autopct='%1.1f%%', startangle=0, shadow=False)

        axcolor = 'lightgoldenrodyellow'

        axfreq = plt.axes([0.35, 0.10, 0.5, 0.02], facecolor=axcolor)
        self.sliderWeightContentWords = Slider(axfreq, 'weightContentWords', 0, 1, valinit=self.weightContentWords,
                                               valstep=0.0001, valfmt="%1.4f")
        self.sliderWeightContentWords.on_changed(self.onUpdateCW)

        axfreq = plt.axes([0.35, 0.13, 0.5, 0.02], facecolor=axcolor)
        self.sliderWeightFctWords = Slider(axfreq, 'weightFctWords', 0, 1, valinit=self.weightFctWords,
                                           valstep=0.0001, valfmt="%1.4f")
        self.sliderWeightFctWords.on_changed(self.onUpdateFW)

        axfreq = plt.axes([0.35, 0.16, 0.5, 0.02], facecolor=axcolor)
        self.sliderWeightMathProps = Slider(axfreq, 'weightMathProps', 0, 1, valinit=self.weightMathProps,
                                            valstep=0.0001, valfmt="%1.4f")
        self.sliderWeightMathProps.on_changed(self.onUpdateMP)

        axfreq = plt.axes([0.35, 0.19, 0.5, 0.02], facecolor=axcolor)
        self.sliderWeightWordsWithDR = Slider(axfreq, 'weightWordsWithDR', 0, 1, valinit=self.weightWordsWithDR,
                                              valstep=0.0001, valfmt="%1.4f")
        self.sliderWeightWordsWithDR.on_changed(self.onUpdateDR)

        axfreq = plt.axes([0.35, 0.22, 0.5, 0.02], facecolor=axcolor)
        self.sliderNbClusters = Slider(axfreq, 'NbClusters', 1, 100, valinit=self.nbClusters,
                                       valstep=1, valfmt="%d")
        self.sliderNbClusters.on_changed(self.onUpdateNbClusters)

        # Pos, size
        axeRight = 0.825
        resetax = plt.axes([0.73, 0.02, 0.075, 0.04])
        self.buttonClusterize = Button(resetax, 'Clusterize', color=axcolor, hovercolor='0.975')
        self.buttonClusterize.on_clicked(self.onPress)

        resetax = plt.axes([axeRight, 0.02, 0.075, 0.04])
        self.buttonQuit = Button(resetax, 'Quit', color=axcolor, hovercolor='0.975')
        self.buttonQuit.on_clicked(self.quit)

        rax = plt.axes([axeRight, 0.8, 0.15, 0.1], facecolor=axcolor)
        radio = RadioButtons(rax, self.algosNames)
        for circle in radio.circles:
            circle.set_radius(0.075)
        radio.on_clicked(self.initClustAlgo)

        cax = plt.axes([axeRight, 0.7, 0.15, 0.05], facecolor=axcolor)
        check = CheckButtons(cax, labels=["Filter EN words"], actives=[self.filterENWords])
        check.on_clicked(self.onCheckFilterWords)

        tax = plt.axes([axeRight, 0.6, 0.15, 0.05], facecolor=axcolor)
        textBox = TextBox(tax, '', initial=self.currentSubmit)
        textBox.on_submit(self.submitWord)

        tax = plt.axes([axeRight, 0.5, 0.15, 0.05], facecolor=axcolor)
        domainBox = TextBox(tax, '', initial=self.currentDomain)
        #domainBox.on_submit(self.submitWord)

        tax = plt.axes([axeRight, 0.4, 0.15, 0.05], facecolor=axcolor)
        rangeBox = TextBox(tax, '', initial=self.currentRange)
        #rangeBox.on_submit(self.submitWord)

        _ = self.fig.text(axeRight, 0.55, s=self.lastClusterFound)

        _ = PieEventHandler(self.pie[0], self.clustersNames, self.centersNames)
        plt.show()

    def onUpdateCW(self, val):
        self.weightContentWords = val
        self.fig.canvas.draw_idle()

    def onUpdateFW(self, val):
        self.weightFctWords = val
        self.fig.canvas.draw_idle()

    def onUpdateMP(self, val):
        self.weightMathProps = val
        self.fig.canvas.draw_idle()

    def onUpdateDR(self, val):
        self.weightWordsWithDR = val
        self.fig.canvas.draw_idle()

    def onPress(self, _):
        self.buttonClusterize.set_active(False)
        self.clusterize("results/gensim/clusters_2.json")
        self.updateDraw()

    def onUpdateNbClusters(self, val):
        self.nbClusters = int(val)
        self.clustAlgo.n_clusters = self.nbClusters
        self.fig.canvas.draw_idle()

    def quit(self, _):
        plt.close()

    def initClustAlgo(self, name):
        if name == "KMeans":
            self.clustAlgo = KMeans()
        elif name == "AgglomerativeClustering":
            self.clustAlgo = AgglomerativeClustering()
        self.algoName = name
        self.clustAlgo.n_clusters = self.nbClusters

    def onCheckFilterWords(self, label):
        self.filterENWords = not self.filterENWords

    def updateInput(self):
        splitted = str_list_lower(split_op_name(self.currentSubmit))
        # TODO : add domain and range
        vecWithDR = self.model.infer_vector(splitted, epochs=10)
        vecCW = vecWithDR  # TODO : compute it
        vecFctWords = get_fct_words_vec(splitted)
        vecMathsProps = np.zeros(7)

        # Concatenate
        vec, _ = self.concatenateVectors(vecWithDR, vecCW, vecFctWords, vecMathsProps, 0)

        iMin = -1
        minSqDist = 9999999
        for i, center in enumerate(self.centersVecs):
            sqDist = sq_dist(vec, center)
            if sqDist < minSqDist:
                minSqDist = sqDist
                iMin = i
        self.lastClusterFound = "Cluster: " + self.centersNames[iMin]
        self.updateDraw()

    def submitWord(self, text):
        prt("DEBUG: Text submit = ", text)
        self.currentSubmit = text
        self.updateInput()

    def submitDomain(self, text):
        prt("DEBUG: Text submit = ", text)
        splitted = str_list_lower(split_op_name(text))
        # TODO : add domain and range
        vecWithDR = self.model.infer_vector(splitted, epochs=10)
        vecCW = vecWithDR  # TODO : compute it
        vecFctWords = get_fct_words_vec(splitted)
        vecMathsProps = np.zeros(7)

        # Concatenate
        vec, _ = self.concatenateVectors(vecWithDR, vecCW, vecFctWords, vecMathsProps, 0)

        iMin = -1
        minSqDist = 9999999
        for i, center in enumerate(self.centersVecs):
            sqDist = sq_dist(vec, center)
            if sqDist < minSqDist:
                minSqDist = sqDist
                iMin = i
        self.currentSubmit = text
        self.lastClusterFound = "Cluster: " + self.centersNames[iMin]
        self.updateDraw()
