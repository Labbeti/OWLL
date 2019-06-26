from PyQt5.QtWidgets import QGroupBox, QWidget, QVBoxLayout, QLabel, QScrollArea
from src.models.ClusteringObserver import ClusteringObserver
from src.controllers.IClusteringController import IClusteringController


class NamesView(ClusteringObserver):
    def __init__(self, parent: QWidget, controller: IClusteringController):
        self.parent = parent
        self.controller = controller

        self.namesWidget = QGroupBox("Cluster Content")
        self.namesLayout = QVBoxLayout()
        self.contentWidget = QLabel()
        self.scrollArea = QScrollArea()

        self.indCluster = -1

        self.initUI()

    def initUI(self):
        self.parent.layout().addWidget(self.namesWidget)

        self.namesWidget.setLayout(self.namesLayout)
        self.namesWidget.setMinimumSize(200, 200)
        self.contentWidget.setContentsMargins(10, 10, 10, 10)
        self.scrollArea.setWidget(self.contentWidget)
        self.scrollArea.setWidgetResizable(True)
        self.namesLayout.addWidget(self.scrollArea)

        self.contentWidget.setWordWrap(True)
        self.contentWidget.setText("")

    def showCluster(self, label: str):
        self.indCluster = -1
        for i, center in enumerate(self.controller.getModelCenters()):
            if center == label:
                self.indCluster = i
                break
        self.updateContent()

    def updateContent(self):
        if self.indCluster != -1:
            clusters = self.controller.getModelClusters()
            centers = self.controller.getModelCenters()
            cluster = clusters[self.indCluster]
            center = centers[self.indCluster]

            self.namesWidget.setTitle("Cluster \"%s\"" % center)
            content = ""
            for name in cluster:
                content += name + ", "
            self.contentWidget.setText(content)
        else:
            self.contentWidget.setText("")

    def onClusteringBegan(self):
        pass

    def onClusteringEnded(self):
        self.updateContent()

    def onModelLoaded(self):
        self.indCluster = -1
        self.updateContent()
