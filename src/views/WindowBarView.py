from PyQt5.QtWidgets import QAction, QMainWindow
from src.controllers.ISaveController import ISaveController


class WindowBarView:
    def __init__(self, window: QMainWindow, saveController: ISaveController):
        self.window = window
        self.saveController = saveController

        self.initUI()

    def initUI(self):
        bar = self.window.menuBar()
        file = bar.addMenu("File")
        loadAct = QAction("Open model", self.window)
        loadAct.setShortcut("Ctrl+O")
        saveAct = QAction("Save model", self.window)
        saveAct.setShortcut("Ctrl+S")
        file.addAction(loadAct)
        file.addAction(saveAct)

        file.triggered[QAction].connect(self.onMenuBarClick)

    def onMenuBarClick(self, act):
        if act.text() == "Open model":
            self.saveController.onOpenModel()
        elif act.text() == "Save model":
            self.saveController.onSaveModel()
        else:
            raise Exception("Unknown action %s." % act.text())
