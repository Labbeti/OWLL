import json
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QWidget
from src.CST import CST
from src.controllers.ISaveController import ISaveController
from src.models.ClusteringModel import ClusteringModel
from src import PROJECT_VERSION


class SaveController(ISaveController):
    def __init__(self, window: QWidget, model: ClusteringModel):
        self.window = window
        self.model = model

    def loadFromFile(self, filepath: str) -> bool:
        """
            Load clustering model from a JSON file.
            :param filepath: Path to JSON file.
            :return: Return True if loading was successfull.
        """
        try:
            fIn = open(filepath, "r", encoding="utf-8")
        except IOError:
            box = QMessageBox()
            box.setWindowTitle("Error")
            box.setIcon(QMessageBox.Warning)
            box.setText("Cannot open file \"%s\"." % filepath)
            box.setStandardButtons(QMessageBox.Ok)
            box.exec_()
            return False

        try:
            data = json.load(fIn)
        except json.decoder.JSONDecodeError:
            box = QMessageBox()
            box.setWindowTitle("Error")
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
        """
            Save current clustering model to JSON file.
            :param filepath: path to JSON file.
        """
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

    def onOpenModel(self):
        """
            Override
        """
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getOpenFileName(
            self.window, "Open model", CST.PATH.MODEL_DIRPATH, "JSON Files (*.json);;All Files (*)", options=options)
        if filepath:
            self.loadFromFile(filepath)

    def onSaveModel(self):
        """
            Override
        """
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self.window, "Save model", CST.PATH.MODEL_DIRPATH, "JSON Files (*.json);;All Files (*)", options=options)
        if filepath:
            if not filepath.endswith(".json"):
                filepath += ".json"
            self.saveInFile(filepath)
