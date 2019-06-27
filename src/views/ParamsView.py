from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QRadioButton, QGroupBox
from src.CST import CST
from src.controllers.IClusteringController import IClusteringController
from src.models.ClusteringObserver import ClusteringObserver
from src.util import dbg


class ParamsView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IClusteringController):
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

        for name in CST.CLUSTERING_ALGORITHMS_NAMES:
            self.radiosButtons.append(QRadioButton(name))
        self.radiosButtons[3].setChecked(True)  # KMeans by default
        for radioButton in self.radiosButtons:
            self.radiosLayout.addWidget(radioButton)
        self.radiosLayout.setSpacing(0)

        self.paramsWidget.setLayout(self.paramsLayout)
        self.paramsLayout.addWidget(self.radiosWidget)
        self.paramsLayout.addWidget(self.deterBox)
        self.paramsLayout.addWidget(self.filterWordBox)

        self.deterBox.setText("Deterministic")
        self.filterWordBox.setText("Filter Non-English words")
        self.filterWordBox.setChecked(True)

        # Note: This function is disabled by default, it does not provide a real determinic results,
        # It allow just a detemrinistic clusterisation but not a deterministic vector inference.
        self.deterBox.hide()

    def setEnabled(self, enable: bool):
        self.paramsWidget.setEnabled(enable)

    def onClusteringBegan(self):
        self.setEnabled(False)

    def onClusteringEnded(self):
        self.setEnabled(True)

    def onModelLoaded(self):
        params = self.controller.getModelParams()
        algoName = params["Algorithm"]
        for radioButton in self.radiosButtons:
            radioButton.setChecked(radioButton.text() == algoName)
        self.deterBox.setChecked(params["Deterministic"])
        self.filterWordBox.setChecked(params["FilterENWords"])

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