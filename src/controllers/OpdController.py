from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox
from src.controllers.IOpdController import IOpdController
from src.CST import CST
from src.models.ontology import OPD


class OpdController(IOpdController):
    def __init__(self, window: QWidget, opd: OPD):
        """
            Constructor of OpdController.
            :param window: the main window of the application.
            :param opd: the OPD of the application.
        """
        IOpdController.__init__(self)

        self.window = window
        self.opd = opd

    def openOpd(self, filepath: str):
        """
            Open OPD from TXT file.
            :param filepath: path to the OPD file to read.
        """
        self.opd.clear()
        self.notifyOpdLoadBegan()
        loaded = self.opd.loadFromFile(filepath)
        self.notifyOpdLoadEnded()
        if loaded:
            self.showOpdLoadSuccessBox("Load of OPD file \"%s\" successfull." % filepath)
        else:
            self.showOpdLoadErrorBox("Load of OPD file \"%s\" failed." % filepath)

    def saveOpd(self, filepath: str):
        """
            Save OPD in a file.
            :param filepath: path to the future OPD file.
        """
        self.opd.saveInFile(filepath, False)

    def genOpdFromDir(self, dirpath: str):
        """
            Generate OPD with a directory.
            :param dirpath: directory path where to search ontologies.
        """
        self.opd.clear()
        self.notifyOpdLoadBegan()
        loaded = self.opd.generateFromDir(dirpath, self)
        self.notifyOpdLoadEnded()
        if loaded:
            self.showOpdLoadSuccessBox("Generation of OPD successfull.")
        else:
            self.showOpdLoadErrorBox("Generation of OPD failed.")

    def genOpdFromFiles(self, filepaths: list):
        """
            Generate OPD with a list of files.
            :param filepaths: filepaths to ontologies.
        """
        self.opd.clear()
        self.notifyOpdLoadBegan()
        loaded = self.opd.generateFromFiles(filepaths, self)
        self.notifyOpdLoadEnded()
        if loaded:
            self.showOpdLoadSuccessBox("Generation of OPD successfull.")
        else:
            self.showOpdLoadErrorBox("Generation of OPD failed.")

    def showOpdLoadSuccessBox(self, message: str):
        """
            Show a information message in a dialog box.
            :param message: the message to display.
        """
        box = QMessageBox()
        box.setWindowTitle("Success")
        box.setIcon(QMessageBox.Information)
        box.setText(message)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()

    def showOpdLoadErrorBox(self, message: str):
        """
            Show a error message in a dialog box.
            :param message: the message to display.
        """
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setIcon(QMessageBox.Warning)
        box.setText(message)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()

    def onOpenOpd(self):
        """
            Override
        """
        filepath, _ = QFileDialog.getOpenFileName(
            self.window, "Open OPD", CST.PATH.OPD_DIRPATH, "Text (*.txt);;All Files (*)")
        if filepath:
            self.openOpd(filepath)

    def onSaveOpd(self):
        """
            Override
        """
        filepath, _ = QFileDialog.getSaveFileName(
            self.window, "Save OPD", CST.PATH.OPD_DIRPATH, "Text Files (*.txt);;All Files (*)")
        if filepath:
            self.saveOpd(filepath)

    def onGenOpdFromDir(self):
        """
            Override
        """
        dirpath = QFileDialog.getExistingDirectory(
            self.window, "Select a directory where to search ontologies...", CST.PATH.ONTOLOGIES)
        if dirpath:
            self.genOpdFromDir(dirpath)

    def onGenOpdFromFiles(self):
        """
            Override
        """
        filepaths, _ = QFileDialog.getOpenFileNames(
            self.window, "Select a list of ontologies files...", CST.PATH.ONTOLOGIES)
        if filepaths:
            self.genOpdFromFiles(filepaths)

    def getOPD(self) -> OPD:
        """
            Override
        """
        return self.opd
