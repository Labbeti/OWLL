from PyQt5.QtWidgets import QAction, QMainWindow
from src.controllers.IOpdController import IOpdController
from src.controllers.ISaveController import ISaveController


class WindowBarView:
    def __init__(self, window: QMainWindow, saveController: ISaveController, opdController: IOpdController):
        self.window = window
        self.saveController = saveController
        self.opdController = opdController

        self.actionsConfig = {
            "Open model": {"fct": self.saveController.onOpenModel, "shortcut": "Ctrl+O"},
            "Save model": {"fct": self.saveController.onSaveModel, "shortcut": "Ctrl+S"},
            "Open opd": {"fct": self.opdController.onOpenOpd},
            "Save opd": {"fct": self.opdController.onSaveOpd},
            "Generate opd from directory": {"fct": self.opdController.onGenOpdFromDir},
            "Generate opd from files": {"fct": self.opdController.onGenOpdFromFiles},
        }

        self.initUI()

    def initUI(self):
        bar = self.window.menuBar()
        file = bar.addMenu("File")

        for name, config in self.actionsConfig.items():
            act = QAction(name, self.window)
            if "shortcut" in config.keys():
                act.setShortcut(config["shortcut"])
            file.addAction(act)
        file.triggered[QAction].connect(self.onMenuBarClick)

    def onMenuBarClick(self, act):
        if act.text() in self.actionsConfig.keys():
            self.actionsConfig[act.text()]["fct"]()
        else:
            raise Exception("Unknown action %s." % act.text())
