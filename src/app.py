import sys

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from src.controllers.ClusteringController import ClusteringController
from src.Csts import Csts
from src.models.ClusteringModel import ClusteringModel
from src.views.OwllWindow import OwllWindow
from src.util import prt


OWLL_VERSION = "0.2.2"


def main():
    prt("Initialize...")
    app = QApplication(sys.argv)
    centralWidget = QWidget()
    centralWidget.setLayout(QHBoxLayout())
    window = OwllWindow()
    window.setCentralWidget(centralWidget)

    model = ClusteringModel(Csts.Paths.ENGLISH_WORDS)
    controller = ClusteringController(model, window)

    window.setController(controller)

    prt("Starting application...")
    # Fit to screen
    window.showMaximized()
    app.exec_()
    prt("Closing application...")
