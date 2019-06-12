from Csts import Csts
from file_io import create_result_file
from ontology.Ontology import Ontology
from time import time
from util import get_filenames
from util import is_unreadable
from util import prt
from util import split_op_name
from util import str_list_lower
import os


def _read_opd_line(line: str) -> list:
    values = line.split("|")
    # Values: ["", "File...", "Op...", ..., "SubPropOf...", "\n"]
    values = values[1:len(values) - 1]
    values = [value.strip() for value in values]
    return values


def _count_unreadables(opNames) -> int:
    count = 0
    for opName in opNames:
        if is_unreadable(opName):
            count += 1
    return count


class OPD:
    COLUMNS_NAMES = ("File", "ObjectProperty", "Domain", "Range", "Asym?", "Func?", "InFu?", "Irre?", "Refl?",
                     "Symm?", "Tran?", "DoIns", "RaIns", "InverseOf", "SubPropertyOf")
    COLUMNS_NAMES_DEBUG = ["Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbTriples", "OpUnreadable",
                           "MustKeep"]
    COLUMNS_NAMES_FORMAT = ("| %-35s " * 4) + ("| %-5s " * 9) + ("| %-35s " * 2) + "| \n"
    LINE_FORMAT = ("| %-35s " * 4) + ("| %-5d " * 9) + ("| %-35s " * 2) + "| \n"
    LINE_FORMAT_DEBUG = "%-40s" + (" %-10s" * len(COLUMNS_NAMES_DEBUG)) + "\n"

    def __init__(self):
        self.__data = []
        self.__debugData = {}
        self.__version = "Unknown"
        self.__srcpath = ""
        self.__filenames = []

    def loadFromFile(self, filepath: str):
        if not os.path.isfile(filepath):
            prt("Error: %s must be a file." % filepath)
            return
        self.clear()
        self.__srcpath = filepath
        file = open(filepath, "r", encoding='utf-8')

        # Read Header
        columnsNames = []
        line = file.readline()
        while line and (line.startswith("#!") or line == "\n"):
            if line.startswith("#! Version: "):
                self.__version = line.split(" ")[2].replace("\n", "")
            elif line.startswith("#! Columns: "):
                line = file.readline()
                columnsNames = _read_opd_line(line)
            line = file.readline()

        if len(columnsNames) == 0:
            raise Exception("Incorrect OPD Header. Missing columns names line.")
        elif len(columnsNames) != len(OPD.COLUMNS_NAMES):
            raise Exception("Incorrect OPD Header. Found %d columns but expected %d." % (
                len(columnsNames), len(OPD.COLUMNS_NAMES)))
        elif self.__version == "Unknown":
            raise Exception("Incorrect OPD Header. Missing version line.")

        # Read data
        self.__data = []
        while line:
            if line != "\n" and not line.startswith("#"):
                values = _read_opd_line(line)
                if values[-1] == "\n":
                    values.pop()  # Remove '\n' at the end of the list
                if len(columnsNames) != len(values):
                    raise Exception("Invalid OPD file \"%s\" at line: \n%s" % (filepath, line))

                valuesDict = {columnsNames[i]: values[i] for i in range(len(values))}
                self.__data.append(valuesDict)
            line = file.readline()

        file.close()

    def generate(self, dirpath: str):
        if not os.path.isdir(dirpath):
            prt("Error: %s must be a directory." % dirpath)
            return

        self.clear()
        self.__srcpath = dirpath

        # Get the filenames of the ontologies
        prt("Search ontologies in \"%s\"" % dirpath)
        self.__filenames = get_filenames(dirpath)

        # Read the list of ontologies
        i = 1
        for filename in self.__filenames:
            # Read the ontology and save data in opd
            start = time()
            prt("Load of \"%s\"... (%d/%d)" % (filename, i, len(self.__filenames)))
            filepath = os.path.join(dirpath, filename)
            ontology = Ontology(filepath)

            if ontology.isLoaded():
                prt("Load of \"%s\" is successfull (RL=%d,OR=%d) (%d/%d)" % (
                    filename, ontology.isLoadedWithRL(), ontology.isLoadedWithOR2(), i, len(self.__filenames)))

                triples = ontology.getOwlTriplesUri()
                for (domainUri, opUri, rangeUri) in triples:
                    domainName = ontology.getName(domainUri)
                    opName = ontology.getName(opUri)
                    rangeName = ontology.getName(rangeUri)

                    opProps = ontology.getOpProperties(opUri)
                    domaimProps = ontology.getClsProperties(domainUri)
                    rangeProps = ontology.getClsProperties(rangeUri)
                    invName = ontology.getName(opProps.inverseOf)
                    parentNames = [ontology.getName(propUri) for propUri in opProps.subPropertyOf]
                    subPropOf = ",".join(parentNames) if len(parentNames) > 0 else ""

                    lineData = [filename, opName, domainName, rangeName, opProps.isAsymmetric, opProps.isFunctional,
                                opProps.isInverseFunctional, opProps.isIrreflexive, opProps.isReflexive,
                                opProps.isSymmetric, opProps.isTransitive, domaimProps.nbInstances,
                                rangeProps.nbInstances, invName, subPropOf]
                    self.__data.append({OPD.COLUMNS_NAMES[i]: lineData[i] for i in range(len(lineData))})
            else:
                triples = []
                prt("Load of \"%s\" has failed (%d/%d)" % (filename, i, len(self.__filenames)))
            end = time()

            nbUnreadable = _count_unreadables([ontology.getName(opUri) for _, opUri, _ in triples])
            self.__debugData["Rdflib?"][filename] = ontology.isLoadedWithRL()
            self.__debugData["Owlready?"][filename] = ontology.isLoadedWithOR2()
            self.__debugData["Loaded?"][filename] = ontology.isLoaded()
            self.__debugData["NbErrors"][filename] = ontology.getNbErrors()
            self.__debugData["Time"][filename] = end - start
            self.__debugData["NbTriples"][filename] = len(triples)
            self.__debugData["OpUnreadable"][filename] = nbUnreadable
            self.__debugData["MustKeep"][filename] = ontology.isLoaded() and nbUnreadable == 0 and len(triples) > 0
            i += 1

    def saveInFile(self, filepath: str, generateDebugFile: bool):
        # Create the OPD file.
        fOpd = create_result_file(filepath)
        fOpd.write(
            "#! Note: Asym = Asymmetric, Func = Functional, InFu = InverseFunctional, Irre = Irreflexive, Refl = "
            "Reflexive, Symm = Symmetric, Tran = Transitive, DoIns = Nb Domain Instances, RaIns = Nb Range Instances\n")
        fOpd.write("\n")
        fOpd.write("#! Columns: \n")
        fOpd.write(OPD.COLUMNS_NAMES_FORMAT % OPD.COLUMNS_NAMES)
        fOpd.write("\n")
        for lineData in self.__data:
            fOpd.write(OPD.LINE_FORMAT % (
                lineData["File"], lineData["ObjectProperty"], lineData["Domain"], lineData["Range"],
                int(lineData["Asym?"]), int(lineData["Func?"]), int(lineData["InFu?"]), int(lineData["Irre?"]),
                int(lineData["Refl?"]), int(lineData["Symm?"]), int(lineData["Tran?"]), int(lineData["DoIns"]),
                int(lineData["RaIns"]), lineData["InverseOf"], lineData["SubPropertyOf"]
            ))
        fOpd.close()

        if generateDebugFile:
            # Generate "opd_debug.txt" file for debugging
            filepathDebug = os.path.join(os.path.dirname(filepath), "opd_debug.txt")
            fDebug = create_result_file(filepathDebug)
            fDebug.write("# Note: If the file is loaded with Rdflib, then it will not try to load with Owlready2.\n\n")
            fDebug.write(OPD.LINE_FORMAT_DEBUG % (
                "File", "Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbTriples", "OpUnreada.", "MustKeep"))
            fDebug.write("\n")

            for filename in self.__filenames:
                time_str = "%-9.2f" % self.__debugData["Time"][filename]
                fDebug.write(OPD.LINE_FORMAT_DEBUG % (
                    filename, self.__debugData["Rdflib?"][filename], self.__debugData["Owlready?"][filename],
                    self.__debugData["Loaded?"][filename], self.__debugData["NbErrors"][filename], time_str,
                    self.__debugData["NbTriples"][filename], self.__debugData["OpUnreadable"][filename],
                    self.__debugData["MustKeep"][filename]))

            fDebug.write("\n")
            time_str = "%-9.2f" % sum(self.__debugData["Time"].values())
            fDebug.write(OPD.LINE_FORMAT_DEBUG % (
                "Total", sum(self.__debugData["Rdflib?"].values()), sum(self.__debugData["Owlready?"].values()),
                sum(self.__debugData["Loaded?"].values()), sum(self.__debugData["NbErrors"].values()), time_str,
                sum(self.__debugData["NbTriples"].values()), sum(self.__debugData["OpUnreadable"].values()),
                sum(self.__debugData["MustKeep"].values())))
            fDebug.write("\n")
            fDebug.write("Nb of files: %d\n" % len(self.__filenames))
            fDebug.close()

    def filter(self, filterFct):
        newData = []
        for values in self.__data:
            if filterFct(values):
                newData.append(values)
        self.__data = newData

    def clear(self):
        self.__data = []
        self.__debugData = {name: {} for name in OPD.COLUMNS_NAMES_DEBUG}
        self.__version = "Unknown"
        self.__srcpath = ""
        self.__filenames = []

    def getData(self) -> list:
        return self.__data

    def getSize(self) -> int:
        return len(self.__data)

    def getSrcpath(self) -> str:
        return self.__srcpath

    def getVersion(self) -> str:
        return self.__version
