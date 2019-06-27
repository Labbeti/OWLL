from PyQt5.QtWidgets import QAction, QMainWindow
from src.controllers.IClusteringController import IClusteringController
from src.controllers.IOpdController import IOpdController
from src.controllers.ISaveController import ISaveController


class WindowBarView:
    def __init__(self, window: QMainWindow, controller: IClusteringController, saveController: ISaveController, opdController: IOpdController):
        self.window = window
        self.controller = controller
        self.saveController = saveController
        self.opdController = opdController

        self.menusConfig = {
            "File": {
                "Exit": {"fct": self.controller.onClose},
            },
            "OPD": {
                "Open OPD": {"fct": self.opdController.onOpenOpd},
                "Generate OPD from directory": {"fct": self.opdController.onGenOpdFromDir},
                "Generate OPD from files": {"fct": self.opdController.onGenOpdFromFiles},
                "Save OPD": {"fct": self.opdController.onSaveOpd},
            },
            "Model": {
                "Open model": {"fct": self.saveController.onOpenModel, "shortcut": "Ctrl+O"},
                "Save model": {"fct": self.saveController.onSaveModel, "shortcut": "Ctrl+S"},
                "Update model": {"fct": self.controller.updateModel, "shortcut": "Ctrl+U"},
            },
        }

        self.initUI()

    def initUI(self):
        bar = self.window.menuBar()

        for menuName, config in self.menusConfig.items():
            menu = bar.addMenu(menuName)
            for name, actionsConfig in config.items():
                act = QAction(name, self.window)
                if "shortcut" in actionsConfig.keys():
                    act.setShortcut(actionsConfig["shortcut"])
                menu.addAction(act)
            menu.triggered[QAction].connect(self.onMenuBarClick)

    def onMenuBarClick(self, act):
        actionName = act.text()
        # Search menu clicked
        fct = None
        for _, config in self.menusConfig.items():
            if actionName in config.keys():
                fct = config[actionName]["fct"]
                break

        if fct is not None:
            fct()
        else:
            raise Exception("Unknown action %s." % act.text())
