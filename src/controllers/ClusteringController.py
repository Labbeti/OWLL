from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow
from src.controllers.IController import IController
from src.models.ClusteringModel import ClusteringModel, ClusteringParameters
from src.views.OptionsView import OptionsView
from src.views.PieView import ViewPie
from src.views.SlidersView import SlidersView
from src.views.TextView import TextView
from src.util import dbg


class ClusteringController(IController):
    def __init__(self, model: ClusteringModel, window: QMainWindow):
        self.model = model
        self.window = window

        self.leftWidget = QWidget()
        self.rightWidget = QWidget()
        # Set layouts
        vBoxLeft = QVBoxLayout()
        vBoxRight = QVBoxLayout()
        vBoxLeft.addStretch()
        # vBoxRight.addStretch()
        self.leftWidget.setLayout(vBoxLeft)
        self.rightWidget.setLayout(vBoxRight)

        self.optionsView = OptionsView(self.leftWidget, self)
        self.pieView = ViewPie(self.rightWidget, self)
        self.slidersView = SlidersView(self.rightWidget, self)
        self.textView = TextView()

        self.initUI()

    def initUI(self):
        self.window.centralWidget().layout().addWidget(self.leftWidget)
        self.window.centralWidget().layout().addWidget(self.rightWidget)

        # Set observers
        self.model.addObs(self.optionsView)
        self.model.addObs(self.pieView)
        self.model.addObs(self.textView)
        self.model.addObs(self.slidersView)

    def updateModel(self):
        params = ClusteringParameters()

        params["Algorithm"] = self.optionsView.getAlgorithmChosen()
        slidersValues = self.slidersView.getSlidersValues()
        for name, value in slidersValues.items():
            params[name] = value
        params["NbClusters"] = int(params["NbClusters"])

        self.model.clustering(params)

    def loadFileModel(self, filepath: str):
        self.model.loadFromFile(filepath)

    def saveFileModel(self, filepath: str):
        self.model.saveInFile(filepath)

    def onClick(self, label: str):
        dbg("Controller : click on ", label)
        self.textView.showCluster(label)

    def getModelParams(self):
        return self.model.getParams()
