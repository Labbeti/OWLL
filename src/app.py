import sys

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from src.controllers.ClusteringController import ClusteringController
from src.controllers.OpdController import OpdController
from src.controllers.SaveController import SaveController
from src.CST import CST
from src.models.ClusteringModel import ClusteringModel
from src.models.ontology.OPD import OPD
from src.views.OwllWindow import OwllWindow
from src.util import prt


def main():
    """
        Main entry of OWLL GUI.
    """
    prt("Starting application...")
    app = QApplication(sys.argv)
    centralWidget = QWidget()
    centralWidget.setLayout(QHBoxLayout())
    window = OwllWindow()
    window.setCentralWidget(centralWidget)

    opd = OPD()
    model = ClusteringModel(opd, CST.PATH.ENGLISH_WORDS)
    saveController = SaveController(window, model)
    opdController = OpdController(window, opd)
    controller = ClusteringController(app, window, model, saveController, opdController)

    window.setController(controller)
    model.setSaveController(saveController)

    # Fit to screen
    window.showMaximized()

    if CST.LOAD_DEFAULTS_FILES:
        opdController.openOpd(CST.PATH.OPD)
        saveController.loadFromFile(CST.PATH.CLUSTER_MODEL)

    app.exec_()
    prt("Closing application...")
