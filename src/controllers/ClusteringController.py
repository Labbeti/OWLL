from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QFileDialog
from src.controllers.IController import IController
from src.models.ClusteringModel import ClusteringModel, ClusteringParameters
from src.views.PieView import ViewPie
from src.views.SlidersView import SlidersView
from src.views.NamesView import NamesView
from src.views.WindowBarView import WindowBarView
from src.views.ButtonsView import ButtonsView
from src.views.ParamsView import ParamsView
from src.views.ProgressView import ProgressView
from src.util import dbg


class ClusteringController(IController):
    def __init__(self, model: ClusteringModel, window: QMainWindow):
        self.model = model
        self.window = window

        self.leftWidget = QWidget()
        self.rightWidget = QWidget()
        self.leftLayout = QVBoxLayout(self.leftWidget)
        self.rightLayout = QVBoxLayout(self.rightWidget)

        self.progressView = ProgressView()
        self.windowBarView = WindowBarView(self.window, self)

        self.paramsView = ParamsView(self.leftWidget, self)
        self.buttonsView = ButtonsView(self.leftWidget, self)

        self.pieView = ViewPie(self.rightWidget, self)
        self.slidersView = SlidersView(self.rightWidget, self)
        self.opsView = NamesView(self.rightWidget, self)

        self.initUI()

    def initUI(self):
        self.window.centralWidget().layout().addWidget(self.leftWidget)
        self.window.centralWidget().layout().addWidget(self.rightWidget)

        self.leftLayout.addStretch()
        self.leftLayout.setSpacing(20)

        # Set observers
        self.model.addObs(self.pieView)
        self.model.addObs(self.opsView)
        self.model.addObs(self.slidersView)
        self.model.addObs(self.buttonsView)
        self.model.addObs(self.paramsView)
        #self.model.addProgressObs(self.progressView)  # TODO : remettre quand les bugs seront corrigés

    def updateModel(self):
        params = ClusteringParameters()

        params["Algorithm"] = self.paramsView.getParamAlgo()
        slidersValues = self.slidersView.getSlidersValues()
        for name, value in slidersValues.items():
            params[name] = value
        params["NbClusters"] = int(params["NbClusters"])
        params["DimOPWithDR"] = int(params["DimOPWithDR"])
        params["DimCW"] = int(params["DimCW"])
        params["DimDR"] = int(params["DimDR"])

        params["Deterministic"] = self.paramsView.getParamDeterministic()
        params["FilterENWords"] = self.paramsView.getParamFilterWords()

        self.model.clustering(params)

    def onOpenModel(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self.window, "Open model", "", "JSON Files (*.json);;All Files (*)", options=options)
        if filepath:
            self.model.loadFromFile(filepath)

    def onSaveModel(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self.window, "Save model", "", "JSON Files (*.json);;All Files (*)", options=options)
        if filepath:
            if not filepath.endswith(".json"):
                filepath += ".json"
            self.model.saveInFile(filepath)

    def onClusterClick(self, label: str):
        self.opsView.showCluster(label)

    def onClose(self):
        self.window.close()

    def getModelParams(self) -> ClusteringParameters:
        return self.model.getParams()

    def getModelClusters(self) -> list:
        return self.model.getClusters()

    def getModelCenters(self) -> list:
        return self.model.getCenters()
