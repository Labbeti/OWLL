from abc import abstractmethod
from src.controllers.OpdSubject import OpdSubject
from src.models.ontology import OPD
from src.ProgressSubject import ProgressSubject


class IOpdController(OpdSubject, ProgressSubject):
    def __init__(self):
        """
            Constructor of IOpdController.
        """
        OpdSubject.__init__(self)
        ProgressSubject.__init__(self)

    @abstractmethod
    def onOpenOpd(self):
        """
            Method called when user is asking for open an OPD.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onSaveOpd(self):
        """
            Method called when user is asking for save an OPD.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onGenOpdFromDir(self):
        """
            Method called when user is asking for generating an OPD with a directory.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onGenOpdFromFiles(self):
        """
            Method called when user is asking for generating an OPD with a list of files.
        """
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getOPD(self) -> OPD:
        """
            Getter of current OPD.
            :return: the current OPD.
        """
        raise NotImplementedError("Abstract method")
