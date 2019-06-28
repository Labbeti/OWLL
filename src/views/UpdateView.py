from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QVBoxLayout, QApplication, QLabel
from src.CST import CST
from src.controllers.IClusteringController import IClusteringController
from src.controllers.IOpdController import IOpdController
from src.controllers.ISaveController import ISaveController
from src.controllers.OpdObserver import OpdObserver
from src.models.ClusteringObserver import ClusteringObserver


class UpdateView(ClusteringObserver, OpdObserver):
    def __init__(
            self, parent: QWidget, controller: IClusteringController, saveController: ISaveController,
            opdController: IOpdController, app: QApplication):
        """
            Constructor of UpdateView.
            :param parent: Parent widget of update view. Must have set his layout.
            :param controller: the clustering controller of the application.
            :param saveController: the save controller of the application.
            :param opdController: the opd controller of the application.
            :param app: the PyQt application object.
        """
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
        """
            Private method for initialize the sliders.
        """
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
        """
            Method called when user want to update model with OPD.
        """
        self.controller.updateModel()

    def onClusteringBegan(self):
        """
            Override
        """
        self.setEnabled(False)
        self.modelStatusLabel.setText("Model not updated.")
        self.modelStatusLabel.setStyleSheet("color: red")
        self.app.processEvents()

    def onClusteringEnded(self):
        """
            Override
        """
        self.setEnabled(True)
        self.modelStatusLabel.setText("Model updated.")
        self.modelStatusLabel.setStyleSheet("color: green")

    def onModelLoaded(self):
        """
            Override
        """
        pass

    def onOpdLoadBegan(self):
        """
            Override
        """
        self.setEnabled(False)
        self.updateOpdStatus()

    def onOpdLoadEnded(self):
        """
            Override
        """
        self.setEnabled(True)
        self.updateOpdStatus()

    def updateOpdStatus(self):
        """
            Private method for update status label.
        """
        if self.opdController.getOPD().isLoaded():
            self.opdStatusLabel.setText("OPD loaded.")
            self.opdStatusLabel.setStyleSheet("color: green")
        else:
            self.opdStatusLabel.setText("OPD not loaded.")
            self.opdStatusLabel.setStyleSheet("color: red")

    def setEnabled(self, enable: bool):
        """
            Activate or deactivate the UpdateView.
            :param enable: True if you want to activate the view.
        """
        self.updateWidget.setEnabled(enable)
        if enable:
            self.updateWidget.setToolTip("Update model")
        else:
            self.updateWidget.setToolTip("OPD must be loaded for update model.")
