import sys

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from src.controllers.ClusteringController import ClusteringController
from src.controllers.SaveController import SaveController
from src.CST import CST
from src.models.ClusteringModel import ClusteringModel
from src.views.OwllWindow import OwllWindow
from src.util import prt


def main():
    prt("Starting application...")
    app = QApplication(sys.argv)
    centralWidget = QWidget()
    centralWidget.setLayout(QHBoxLayout())
    window = OwllWindow()
    window.setCentralWidget(centralWidget)

    model = ClusteringModel(CST.PATH.OPD, CST.PATH.ENGLISH_WORDS)
    saveController = SaveController(window, model)
    controller = ClusteringController(app, window, model, saveController)

    window.setController(controller)
    model.setSaveController(saveController)

    # Fit to screen
    window.showMaximized()
    app.exec_()
    prt("Closing application...")
