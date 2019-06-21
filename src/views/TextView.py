from PyQt5.QtWidgets import QMainWindow, QLabel, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from src.models.ClusteringModel import ClusteringObserver
from src.util import dbg


class TextView(ClusteringObserver):
    def __init__(self):
        self.window = QMainWindow()
        self.centralWidget = QWidget()
        self.layout = QHBoxLayout()
        self.text = QLabel()

        self.clustersNames = []
        self.centersNames = []
        self.indCluster = -1

        self.initUI()

    def initUI(self):
        self.centralWidget.setLayout(self.layout)
        self.layout.addStretch()
        self.layout.addWidget(self.text)
        self.window.setCentralWidget(self.centralWidget)
        self.window.show()
        self.layout.setAlignment(Qt.AlignCenter)
        self.text.setAlignment(Qt.AlignCenter)

    def onClusteringEnded(self, clustersNames, centersNames):
        self.text.setText("")
        self.clustersNames = clustersNames
        self.centersNames = centersNames
        self.indCluster = -1

    def showCluster(self, label: str):
        self.indCluster = -1
        for i, center in enumerate(self.centersNames):
            if center == label:
                self.indCluster = i
                break

        if self.indCluster != -1:
            dbg("Show cluster %d, %s" % (self.indCluster, label))
            cluster = self.clustersNames[self.indCluster]

            # TODO : improve for more readability
            nbNamesLimit = 30
            content = ""
            for i, name in enumerate(cluster[:nbNamesLimit]):
                content += name if name != label else "<b>" + name + "</b>"
                content += ", "
                if (i+1) % 5 == 0:
                    content += "<br>"
            if len(cluster) > nbNamesLimit:
                content += "[...]"
            self.text.setText(content)
