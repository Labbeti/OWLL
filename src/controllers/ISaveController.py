from abc import abstractmethod


class ISaveController:
    @abstractmethod
    def onOpenModel(self):
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onSaveModel(self):
        raise NotImplementedError("Abstract method")
