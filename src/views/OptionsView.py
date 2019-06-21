from PyQt5.QtWidgets import QPushButton, QFileDialog, QVBoxLayout, QRadioButton, QWidget
from src.util import dbg
from src.controllers.IController import IController
from src.models.ClusteringModel import ClusteringObserver


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


class OptionsView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IController):
        self.parent = parent
        self.controller = controller

        self.optWidget = QWidget()
        self.optLayout = QVBoxLayout(self.optWidget)

        self.radiosWidget = QWidget()
        self.radiosLayout = QVBoxLayout(self.radiosWidget)
        self.radiosButtons = []
        self.buttonsNames = ["Update model", "Load model", "Save model", "Quit"]
        self.buttons = {}
        for name in self.buttonsNames:
            self.buttons[name] = QPushButton(name)

        self.initUI()

    def initUI(self):
        self.parent.layout().addWidget(self.optWidget)

        for name in CLUSTERING_ALGORITHMS_NAMES:
            self.radiosButtons.append(QRadioButton(name))
        self.radiosButtons[3].setChecked(True)  # KMeans by default
        for radioButton in self.radiosButtons:
            self.radiosLayout.addWidget(radioButton)
        self.radiosLayout.setSpacing(10)

        self.optLayout.addWidget(self.radiosWidget)
        for button in self.buttons.values():
            self.optLayout.addWidget(button)

        self.buttons["Update model"].clicked.connect(self.onButtonUpdateModel)
        self.buttons["Load model"].clicked.connect(self.onButtonLoad)
        self.buttons["Save model"].clicked.connect(self.onButtonSave)
        self.buttons["Quit"].clicked.connect(self.onButtonQuit)
        # TODO self.buttonQuit.setToolTip("Leaving the application without saving.")

    def onButtonUpdateModel(self):
        for button in self.buttons.values():
            button.setEnabled(False)
        self.controller.updateModel()

    def onButtonLoad(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self.parent, "Load model", "", "JSON Files (*.json);;All Files (*);;", options=options)
        if filepath:
            self.controller.loadFileModel(filepath)

    def onButtonSave(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self.parent, "Save model", "", "JSON Files (*.json);;All Files (*);;", options=options)
        if filepath:
            self.controller.saveFileModel(filepath)

    def onButtonQuit(self):
        self.parent.window().close()

    def onClusteringEnded(self, clustersNames, centersNames):
        dbg("Options View: enable buttons...")
        for button in self.buttons.values():
            button.setEnabled(True)

    def getAlgorithmChosen(self) -> str:
        clustAlgo = "NoAlgoChecked"
        for radioButton in self.radiosButtons:
            if radioButton.isChecked():
                clustAlgo = radioButton.text()
        return clustAlgo
