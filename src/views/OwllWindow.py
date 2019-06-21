from PyQt5.QtWidgets import QMainWindow
from abc import abstractmethod

from src.util import dbg


class WindowObserver:
    @abstractmethod
    def onWindowResized(self, newSize):
        raise Exception("Not implemented")


class WindowSubject:
    def __init__(self):
        self.views = []

    def addObs(self, obs: WindowObserver):
        self.views.append(obs)

    def notifyResized(self, size):
        for view in self.views:
            view.onWindowResized(size)


class OwllWindow(QMainWindow, WindowSubject):
    def __init__(self):
        super().__init__()
        # Init attributes
        self.title = 'OWLL'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

    def resizeEvent(self, *args, **kwargs):
        dbg("Window resized")
        super().resizeEvent(*args, **kwargs)
        self.notifyResized(self.size())
