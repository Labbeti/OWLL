from abc import abstractmethod


class OpdObserver:
    @abstractmethod
    def onOpdLoadBegan(self):
        """
            Method called when OPD is clear and just before the beginning of OPD from file(s).
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onOpdLoadEnded(self):
        """
            Method called after the OPD file has finished to load without known if the loading is successfull.
        """
        raise NotImplementedError("Abstract method")
