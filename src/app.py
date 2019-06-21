import sys

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from src.controllers.ClusteringController import ClusteringController
from src.models.ClusteringModel import ClusteringModel
from src.views.OwllWindow import OwllWindow
from src.util import prt


def main():
    prt("Initialize...")
    app = QApplication(sys.argv)
    centralWidget = QWidget()
    centralWidget.setLayout(QHBoxLayout())
    window = OwllWindow()
    window.setCentralWidget(centralWidget)

    model = ClusteringModel()
    _ = ClusteringController(model, window)

    prt("Starting application...")
    # Fit to screen
    window.showMaximized()
    app.exec_()
    prt("Closing application...")
