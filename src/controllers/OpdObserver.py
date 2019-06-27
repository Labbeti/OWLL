from abc import abstractmethod


class OpdObserver:
    @abstractmethod
    def onOpdLoadBegan(self):
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onOpdLoadEnded(self):
        raise NotImplementedError("Abstract method")
