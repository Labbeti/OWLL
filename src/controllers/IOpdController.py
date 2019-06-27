from abc import abstractmethod
from src.controllers.OpdSubject import OpdSubject
from src.models.ontology import OPD
from src.ProgressSubject import ProgressSubject


class IOpdController(OpdSubject, ProgressSubject):
    def __init__(self):
        OpdSubject.__init__(self)
        ProgressSubject.__init__(self)

    @abstractmethod
    def onOpenOpd(self):
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onSaveOpd(self):
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onGenOpdFromDir(self):
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def onGenOpdFromFiles(self):
        raise NotImplementedError("Abstract method")

    @abstractmethod
    def getOPD(self) -> OPD:
        raise NotImplementedError("Abstract method")
