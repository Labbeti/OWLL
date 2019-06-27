from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QVBoxLayout, QApplication, QLabel
from src.CST import CST
from src.controllers.IClusteringController import IClusteringController
from src.controllers.IOpdController import IOpdController
from src.controllers.ISaveController import ISaveController
from src.controllers.OpdObserver import OpdObserver
from src.models.ClusteringObserver import ClusteringObserver
from src.util import dbg


class UpdateView(ClusteringObserver, OpdObserver):
    def __init__(
            self, parent: QWidget, controller: IClusteringController, saveController: ISaveController,
            opdController: IOpdController, app: QApplication):
        self.parent = parent
        self.controller = controller
        self.saveController = saveController
        self.opdController = opdController
        self.app = app

        self.updateWidget = QGroupBox()
        self.updateLayout = QVBoxLayout()
        self.buttonsConfig = {
            "Update model": self.onButtonUpdateModel,
        }
        self.buttons = {}
        self.opdStatusLabel = QLabel()
        self.modelStatusLabel = QLabel()

        self.initUI()

    def initUI(self):
        self.parent.layout().addWidget(self.updateWidget)
        self.updateWidget.setLayout(self.updateLayout)

        for name, fct in self.buttonsConfig.items():
            button = QPushButton(name)
            self.buttons[name] = button
            self.updateLayout.addWidget(button)
            button.setMinimumHeight(CST.GUI.BUTTON_MIN_HEIGHT)
            button.clicked.connect(fct)

        self.updateLayout.addWidget(self.opdStatusLabel)
        self.updateLayout.addWidget(self.modelStatusLabel)

        self.opdStatusLabel.setText("OPD not loaded.")
        self.opdStatusLabel.setStyleSheet("color: red")
        self.modelStatusLabel.setText("Model not updated.")
        self.modelStatusLabel.setStyleSheet("color: red")
        self.setEnabled(False)

    def onButtonUpdateModel(self):
        self.controller.updateModel()

    def onClusteringBegan(self):
        self.setEnabled(False)
        self.modelStatusLabel.setText("Model not updated.")
        self.modelStatusLabel.setStyleSheet("color: red")
        self.app.processEvents()

    def onClusteringEnded(self):
        self.setEnabled(True)
        self.modelStatusLabel.setText("Model updated.")
        self.modelStatusLabel.setStyleSheet("color: green")

    def onModelLoaded(self):
        dbg("onModelLoaded")
        pass

    def onOpdLoadBegan(self):
        dbg("onOpdLoadBegan")
        self.setEnabled(False)
        self.updateOpdStatus()

    def onOpdLoadEnded(self):
        dbg("onOpdLoadEnded")
        self.setEnabled(True)
        self.updateOpdStatus()

    def updateOpdStatus(self):
        if self.opdController.getOPD().isLoaded():
            self.opdStatusLabel.setText("OPD loaded.")
            self.opdStatusLabel.setStyleSheet("color: green")
        else:
            self.opdStatusLabel.setText("OPD not loaded.")
            self.opdStatusLabel.setStyleSheet("color: red")

    def setEnabled(self, enable: bool):
        self.updateWidget.setEnabled(enable)
        if enable:
            self.updateWidget.setToolTip("Update model")
        else:
            self.updateWidget.setToolTip("OPD must be loaded for update model.")
