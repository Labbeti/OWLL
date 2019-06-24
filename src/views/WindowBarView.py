from PyQt5.QtWidgets import QAction, QMainWindow
from src.controllers.IController import IController


class WindowBarView:
    def __init__(self, window: QMainWindow, controller: IController):
        self.window = window
        self.controller = controller

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
            self.controller.onOpenModel()
        elif act.text() == "Save model":
            self.controller.onSaveModel()
        else:
            raise Exception("Unknown action %s." % act.text())
