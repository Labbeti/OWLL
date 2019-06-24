from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QRadioButton, QGroupBox
from src.controllers.IController import IController
from src.models.ClusteringObserver import ClusteringObserver
from src.util import dbg

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


class ParamsView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IController):
        self.parent = parent
        self.controller = controller

        self.paramsWidget = QGroupBox()
        self.paramsLayout = QVBoxLayout()

        self.radiosWidget = QWidget()
        self.radiosLayout = QVBoxLayout(self.radiosWidget)
        self.radiosButtons = []
        self.deterBox = QCheckBox()
        self.filterWordBox = QCheckBox()

        self.initUI()

    def initUI(self):
        self.parent.layout().addWidget(self.paramsWidget)
        self.deterBox.hide()

        for name in CLUSTERING_ALGORITHMS_NAMES:
            self.radiosButtons.append(QRadioButton(name))
        self.radiosButtons[3].setChecked(True)  # KMeans by default
        for radioButton in self.radiosButtons:
            self.radiosLayout.addWidget(radioButton)
        self.radiosLayout.setSpacing(5)

        self.paramsWidget.setLayout(self.paramsLayout)
        self.paramsLayout.addWidget(self.radiosWidget)
        self.paramsLayout.addWidget(self.deterBox)
        self.paramsLayout.addWidget(self.filterWordBox)

        self.deterBox.setText("Deterministic")
        self.filterWordBox.setText("Filter Non-English words")

    def onClusteringEnded(self):
        pass

    def onModelLoaded(self):
        # TODO : update interface, update check boxes
        params = self.controller.getModelParams()
        dbg("ParamsView: onModelLoaded")
        algoName = params["Algorithm"]
        for radioButton in self.radiosButtons:
            radioButton.setChecked(radioButton.text() == algoName)

    def getParamAlgo(self) -> str:
        clustAlgo = "NoAlgoSelected"
        for radioButton in self.radiosButtons:
            if radioButton.isChecked():
                clustAlgo = radioButton.text()
        return clustAlgo

    def getParamDeterministic(self) -> bool:
        return self.deterBox.isChecked()

    def getParamFilterWords(self) -> bool:
        return self.filterWordBox.isChecked()