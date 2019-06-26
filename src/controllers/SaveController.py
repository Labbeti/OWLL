import json
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QWidget
from src.controllers.ISaveController import ISaveController
from src.models.ClusteringModel import ClusteringModel
from src import PROJECT_VERSION


class SaveController(ISaveController):
    def __init__(self, window: QWidget, model: ClusteringModel):
        self.window = window
        self.model = model

    def onOpenModel(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self.window, "Open model", "", "JSON Files (*.json);;All Files (*)", options=options)
        if filepath:
            self.loadFromFile(filepath)

    def onSaveModel(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self.window, "Save model", "", "JSON Files (*.json);;All Files (*)", options=options)
        if filepath:
            if not filepath.endswith(".json"):
                filepath += ".json"
            self.saveInFile(filepath)

    def loadFromFile(self, filepath: str) -> bool:
        try:
            fIn = open(filepath, "r", encoding="utf-8")
        except IOError:
            box = QMessageBox()
            box.setIcon(QMessageBox.Warning)
            box.setText("Cannot open file \"%s\"." % filepath)
            box.setStandardButtons(QMessageBox.Ok)
            box.exec_()
            return False

        try:
            data = json.load(fIn)
        except json.decoder.JSONDecodeError:
            box = QMessageBox()
            box.setIcon(QMessageBox.Warning)
            box.setText("File \"%s\" is not a valid JSON model file." % filepath)
            box.setStandardButtons(QMessageBox.Ok)
            box.exec_()
            return False

        clustersData = data["clusters"]
        clustersNames = []
        centersNames = []
        for clusterData in clustersData:
            clustersNames.append(clusterData["names"])
            centersNames.append(clusterData["center"])

        fIn.close()
        self.model.setParams(data["params"])
        self.model.setClustersNames(clustersNames)
        self.model.setCentersNames(centersNames)
        self.model.notifyModelLoaded()
        return True

    def saveInFile(self, filepath: str):
        data = dict()
        metaData = dict()
        metaData["OwllVersion"] = PROJECT_VERSION
        data["meta"] = metaData
        data["params"] = self.model.getParams()

        clustersData = []
        for i, (cluster, center) in enumerate(zip(self.model.getClusters(), self.model.getCenters())):
            clusterData = dict()
            clusterData["center"] = center
            clusterData["names"] = cluster
            clustersData.append(clusterData)
        data["clusters"] = clustersData

        fOut = open(filepath, "w", encoding="utf-8")
        json.dump(data, fOut, ensure_ascii=False, indent=4)
        fOut.close()
