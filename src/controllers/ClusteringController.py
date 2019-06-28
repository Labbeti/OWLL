from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QApplication, QMessageBox
from src.controllers.IClusteringController import IClusteringController
from src.controllers.IOpdController import IOpdController
from src.controllers.ISaveController import ISaveController
from src.models.ClusteringModel import ClusteringModel, ClusteringParameters
from src.views.UpdateView import UpdateView
from src.views.InputView import InputView
from src.views.NamesView import NamesView
from src.views.ParamsView import ParamsView
from src.views.PieView import PieView
from src.views.ProgressView import ProgressView
from src.views.SlidersView import SlidersView
from src.views.WindowBarView import WindowBarView


class ClusteringController(IClusteringController):
    """
        ClusteringController
        This class is used in MVC pattern in order to manages views and control user inputs.
    """

    def __init__(self, app: QApplication, window: QMainWindow, model: ClusteringModel, saveController: ISaveController,
                 opdController: IOpdController):
        """
            Constructor of ClusteringController.
            :param app: The QApplication.
            :param window: The Owll window of this project.
            :param model: The model with clusters.
            :param saveController: Another controller for save system.
            :param opdController: Another controller for OPD.
        """
        self.app = app
        self.window = window
        self.model = model
        self.saveController = saveController
        self.opdController = opdController

        self.clustWidget = QWidget()
        self.submitWidget = QWidget()
        self.resultShowWidget = QWidget()

        self.clustLayout = QVBoxLayout(self.clustWidget)
        self.submitLayout = QVBoxLayout(self.submitWidget)
        self.resultShowLayout = QVBoxLayout(self.resultShowWidget)

        self.progressView = ProgressView(app)
        self.windowBarView = WindowBarView(window, self, saveController, opdController)

        self.paramsView = ParamsView(self.clustWidget, self)
        self.slidersView = SlidersView(self.clustWidget, self)
        self.updateView = UpdateView(self.clustWidget, self, saveController, opdController, app)

        self.inputView = InputView(self.submitWidget, self)

        self.pieView = PieView(self.resultShowWidget, self)
        self.opsView = NamesView(self.resultShowWidget, self)

        self.initUI()

    def initUI(self):
        """
            Private method for initilize interfaces.
        """
        centralLayout = self.window.centralWidget().layout()
        centralLayout.addWidget(self.clustWidget, 1)
        centralLayout.addWidget(self.submitWidget, 1)
        centralLayout.addWidget(self.resultShowWidget, 4)
        self.resultShowLayout.setStretch(0, 2)
        self.resultShowLayout.setStretch(1, 1)

        self.clustLayout.addStretch()
        self.submitLayout.addStretch()

        # Set observers
        self.model.addObs(self.pieView)
        self.model.addObs(self.opsView)
        self.model.addObs(self.slidersView)
        self.model.addObs(self.updateView)
        self.model.addObs(self.paramsView)
        self.model.addObs(self.inputView)
        self.model.addObs(self.progressView)
        self.model.addProgressObs(self.progressView)
        self.opdController.addOpdObs(self.progressView)
        self.opdController.addOpdObs(self.updateView)
        self.opdController.addProgressObs(self.progressView)

    def updateModel(self):
        """
            Override
        """
        if not self.opdController.getOPD().isLoaded():
            box = QMessageBox()
            box.setIcon(QMessageBox.Warning)
            box.setText("Cannot update model: OPD is not loaded.")
            box.setStandardButtons(QMessageBox.Ok)
            box.exec_()
            return

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

    def submitOpToModel(self, opName: str, domain: str, range_: str, mathProps: dict):
        """
            Override
        """
        self.model.submitOp(opName, domain, range_, mathProps)

    def onClusterClick(self, label: str):
        """
            Override
        """
        self.opsView.showCluster(label)

    def onClose(self):
        """
            Override
        """
        self.window.close()

    def getModelParams(self) -> ClusteringParameters:
        """
            Override
        """
        return self.model.getParams()

    def getModelClusters(self) -> list:
        """
            Override
        """
        return self.model.getClusters()

    def getModelCenters(self) -> list:
        """
            Override
        """
        return self.model.getCenters()
