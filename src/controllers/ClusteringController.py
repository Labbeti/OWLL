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

        self.leftWidget = QWidget()
        self.rightWidget = QWidget()
        self.leftLayout = QVBoxLayout(self.leftWidget)
        self.rightLayout = QVBoxLayout(self.rightWidget)

        self.progressView = ProgressView(app)
        self.windowBarView = WindowBarView(window, saveController, opdController)

        self.paramsView = ParamsView(self.leftWidget, self)
        self.updateView = UpdateView(self.leftWidget, self, saveController, opdController, app)
        self.inputView = InputView(self.leftWidget, self)

        self.pieView = PieView(self.rightWidget, self)
        self.slidersView = SlidersView(self.rightWidget, self)
        self.opsView = NamesView(self.rightWidget, self)

        self.initUI()

    def initUI(self):
        """
            Private method for initilize interfaces.
        """
        centralLayout = self.window.centralWidget().layout()
        centralLayout.addWidget(self.leftWidget, 1)
        centralLayout.addWidget(self.rightWidget, 9)
        self.rightLayout.setStretch(0, 4)
        self.rightLayout.setStretch(1, 1)
        self.rightLayout.setStretch(2, 4)

        self.leftLayout.addStretch()
        self.leftLayout.setSpacing(20)

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
        self.model.submitOp(opName, domain, range_, mathProps)

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
