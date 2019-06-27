from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox
from src.controllers.IOpdController import IOpdController
from src.models.ontology import OPD


class OpdController(IOpdController):
    def __init__(self, window: QWidget, opd: OPD):
        IOpdController.__init__(self)

        self.window = window
        self.opd = opd

    def openOpd(self, filepath: str):
        self.opd.clear()
        self.notifyOpdLoadBegan()
        loaded = self.opd.loadFromFile(filepath)
        self.notifyOpdLoadEnded()
        if loaded:
            self.showOpdLoadSuccessBox("Load of OPD file \"%s\" successfull." % filepath)
        else:
            self.showOpdLoadErrorBox("Load of OPD file \"%s\" failed." % filepath)

    def saveOpd(self, filepath: str):
        self.opd.saveInFile(filepath, False)

    def genOpdFromDir(self, dirpath: str):
        self.opd.clear()
        self.notifyOpdLoadBegan()
        loaded = self.opd.generateFromDir(dirpath, self)
        self.notifyOpdLoadEnded()
        if loaded:
            self.showOpdLoadSuccessBox("Generation of OPD successfull.")
        else:
            self.showOpdLoadErrorBox("Generation of OPD failed.")

    def genOpdFromFiles(self, filepaths: list):
        self.opd.clear()
        self.notifyOpdLoadBegan()
        loaded = self.opd.generateFromFiles(filepaths, self)
        self.notifyOpdLoadEnded()
        if loaded:
            self.showOpdLoadSuccessBox("Generation of OPD successfull.")
        else:
            self.showOpdLoadErrorBox("Generation of OPD failed.")

    def onOpenOpd(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self.window, "Open OPD", "", "Text (*.txt);;All Files (*)")
        if filepath:
            self.openOpd(filepath)

    def onSaveOpd(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self.window, "Save OPD", "", "Text Files (*.txt);;All Files (*)")
        if filepath:
            self.saveOpd(filepath)

    def onGenOpdFromDir(self):
        dirpath = QFileDialog.getExistingDirectory(self.window, "Select a directory where to search ontologies...")
        if dirpath:
            self.genOpdFromDir(dirpath)

    def onGenOpdFromFiles(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self.window, "Select a list of ontologies files...")
        if filepaths:
            self.genOpdFromFiles(filepaths)

    def showOpdLoadSuccessBox(self, message: str):
        box = QMessageBox()
        box.setWindowTitle("Success")
        box.setIcon(QMessageBox.Information)
        box.setText(message)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()

    def showOpdLoadErrorBox(self, message: str):
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setIcon(QMessageBox.Warning)
        box.setText(message)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()

    def getOPD(self) -> OPD:
        return self.opd
