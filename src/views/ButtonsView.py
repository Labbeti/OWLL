from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QVBoxLayout
from src.controllers.IController import IController
from src.models.ClusteringObserver import ClusteringObserver


class ButtonsView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IController):
        self.parent = parent
        self.controller = controller

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
            button.clicked.connect(fct)

    def onButtonUpdateModel(self):
        for button in self.buttons.values():
            button.setEnabled(False)
        self.controller.updateModel()

    def onButtonLoad(self):
        self.controller.onOpenModel()

    def onButtonSave(self):
        self.controller.onSaveModel()

    def onButtonQuit(self):
        self.controller.onClose()

    def onClusteringEnded(self):
        for button in self.buttons.values():
            button.setEnabled(True)

    def onModelLoaded(self):
        pass
