from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QVBoxLayout, QApplication
from src.CST import CST
from src.controllers.IClusteringController import IClusteringController
from src.controllers.ISaveController import ISaveController
from src.models.ClusteringObserver import ClusteringObserver


class ButtonsView(ClusteringObserver):
    def __init__(
            self, parent: QWidget, controller: IClusteringController, saveController: ISaveController, app: QApplication):
        self.parent = parent
        self.controller = controller
        self.saveController = saveController
        self.app = app

        self.buttonsWidget = QGroupBox()
        self.buttonsLayout = QVBoxLayout()
        self.buttonsConfig = {
            "Update model": self.onButtonUpdateModel,
            "Load model": self.onButtonLoad,
            "Save model": self.onButtonSave,
            "Quit": self.onButtonQuit,
        }
        self.buttons = {}

        self.initUI()

    def initUI(self):
        self.parent.layout().addWidget(self.buttonsWidget)
        self.buttonsWidget.setLayout(self.buttonsLayout)

        for name, fct in self.buttonsConfig.items():
            button = QPushButton(name)
            self.buttons[name] = button
            self.buttonsLayout.addWidget(button)
            button.setMinimumHeight(CST.GUI.BUTTON_MIN_HEIGHT)
            button.clicked.connect(fct)

    def onButtonUpdateModel(self):
        self.controller.updateModel()

    def onButtonLoad(self):
        self.saveController.onOpenModel()

    def onButtonSave(self):
        self.saveController.onSaveModel()

    def onButtonQuit(self):
        self.controller.onClose()

    def onClusteringBegan(self):
        self.setEnabled(False)
        self.app.processEvents()

    def onClusteringEnded(self):
        self.setEnabled(True)

    def onModelLoaded(self):
        pass

    def setEnabled(self, enable: bool):
        self.buttonsWidget.setEnabled(enable)
