from abc import abstractmethod


class ISaveController:
    @abstractmethod
    def onOpenModel(self):
        """
            Method called when clustering model has been loaded.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onSaveModel(self):
        """
            Method called when clustering model has been saved.
        """
        raise NotImplementedError("Abstract method")
