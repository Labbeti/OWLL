from src.file_io import create_result_file
from src.ontology.Ontology import Ontology
from src.ontology.OpData import OpData
from time import time
from src.util import get_filenames
from src.util import iri_to_name
from src.util import is_unreadable
from src.util import prt
from src.util import rem_duplicates

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


def _valuesToOpData(values: dict) -> OpData:
    opData = OpData(src=values["File"])
    opData.inverseOfIri = values["InverseOfIRI"]
    opData.label = ""  # label is not saved in OPD
    opData.domainsIris = values["DomainsIRIs"].split(",")
    opData.rangesIris = values["RangesIRIs"].split(",")
    opData.subPropertyOfIris = values["SubPropertyOfIRIs"].split(",")
    opData.iri = values["OpIRI"]
    opData.nbInstDomains = [int(nbInst) for nbInst in values["DoIns"].split(",")]
    opData.nbInstRanges = [int(nbInst) for nbInst in values["RaIns"].split(",")]
    opData.asymmetric = bool(values["Asym?"])
    opData.functional = bool(values["Func?"])
    opData.inverseFunctional = bool(values["InFu?"])
    opData.irreflexive = bool(values["Irre?"])
    opData.reflexive = bool(values["Refl?"])
    opData.symmetric = bool(values["Symm?"])
    opData.transitive = bool(values["Tran?"])
    return opData


def _opDataToValues(opData: OpData) -> dict:
    domainsIris = ",".join(opData.getDomainsIris())
    domainsNames = ",".join([iri_to_name(iri) for iri in opData.getDomainsIris()])
    rangesIris = ",".join(opData.getRangesIris())
    rangesNames = ",".join([iri_to_name(iri) for iri in opData.getRangesIris()])

    inverseOfName = iri_to_name(opData.getInverseOfIri()) if opData.getInverseOfIri() != "" \
        else ""
    subPropertyOfIRIs = ",".join(opData.getSubPropertyOfIris())
    subPropertyOfNames = \
        ",".join([iri_to_name(iri) for iri in opData.getSubPropertyOfIris()])

    nbInstDo = ",".join([str(nbInst) for nbInst in opData.nbInstDomains])
    nbInstRa = ",".join([str(nbInst) for nbInst in opData.nbInstRanges])

    lineData = [
        opData.src, opData.getName(), domainsNames, rangesNames, inverseOfName, subPropertyOfNames,
        nbInstDo, nbInstRa, opData.isAsymmetric(), opData.isFunctional(), opData.isInverseFunctional(),
        opData.isIrreflexive(), opData.isReflexive(), opData.isSymmetric(), opData.isTransitive(),
        opData.getIri(), domainsIris, rangesIris, opData.getInverseOfIri(), subPropertyOfIRIs
    ]
    return {OPD.COLUMNS_NAMES[i]: lineData[i] for i in range(len(lineData))}


class OpdParseError(Exception):
    pass


class OPD:
    COLUMNS_NAMES = (
        "File", "ObjectProperty", "Domains", "Ranges", "InverseOf", "SubPropertyOf", "DoIns", "RaIns", "Asym?",
        "Func?", "InFu?", "Irre?", "Refl?", "Symm?", "Tran?", "OpIRI", "DomainsIRIs", "RangesIRIs", "InverseOfIRI",
        "SubPropertyOfIRIs")
    COLUMNS_NAMES_DEBUG = [
        "Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbOp", "OpUnreadable", "MustKeep"]
    COLUMNS_NAMES_FORMAT = \
        ("| %-40s " * 6) + ("| %-5s " * 2) + ("| %-5s " * 7) + ("| %-100s " * 5) + "| \n"
    LINE_FORMAT = \
        ("| %-40s " * 6) + ("| %-5s " * 2) + ("| %-5d " * 7) + ("| %-100s " * 5) + "| \n"
    LINE_FORMAT_DEBUG = "%-40s" + (" %-10s" * len(COLUMNS_NAMES_DEBUG)) + "\n"

    def __init__(self):
        self.__data = []
        self.__debugData = {}
        self.__version = "Unknown"
        self.__srcpath = ""
        self.__filenames = []

    def generate(self, dirpath: str):
        """
            Generate the OPD with a list of OWL files. Can take a long time with the 178 ontologies (~30min).
            :param dirpath: Path where to search ontologies.
        """
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
                for opData in ontology.getAllOpsData().values():
                    self.__data.append(opData)

            else:
                prt("Load of \"%s\" has failed (%d/%d)" % (filename, i, len(self.__filenames)))
            end = time()

            nbUnreadable = _count_unreadables([opData.name for opData in ontology.getAllOpsData().values()])
            self.__debugData["Rdflib?"][filename] = ontology.isLoadedWithRL()
            self.__debugData["Owlready?"][filename] = ontology.isLoadedWithOR2()
            self.__debugData["Loaded?"][filename] = ontology.isLoaded()
            self.__debugData["NbErrors"][filename] = ontology.getNbErrors()
            self.__debugData["Time"][filename] = end - start
            self.__debugData["NbOp"][filename] = len(ontology.getAllOpsData())
            self.__debugData["OpUnreadable"][filename] = nbUnreadable
            self.__debugData["MustKeep"][filename] = \
                ontology.isLoaded() and nbUnreadable == 0 and len(ontology.getAllOpsData()) > 0
            i += 1

    def loadFromFile(self, filepath: str):
        """
            Load the OPD from a TXT file.
            Can raise exception "OpdParseError" if the file format is incorrect.
            :param filepath: Path to the file to read.
        """
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
            raise OpdParseError("Incorrect OPD Header. Missing columns names line.")
        elif len(columnsNames) != len(OPD.COLUMNS_NAMES):
            raise OpdParseError("Incorrect OPD Header. Found %d columns but expected %d." % (
                len(columnsNames), len(OPD.COLUMNS_NAMES)))
        elif self.__version == "Unknown":
            raise OpdParseError("Incorrect OPD Header. Missing version line.")

        # Read data
        self.__data = []
        while line:
            if line != "\n" and not line.startswith("#"):
                values = _read_opd_line(line)
                if values[-1] == "\n":
                    values.pop()  # Remove '\n' at the end of the list
                if len(columnsNames) != len(values):
                    raise OpdParseError("Invalid OPD file \"%s\" at line: \n%s" % (filepath, line))

                valuesDict = {columnsNames[i]: values[i] for i in range(len(values))}

                opData = _valuesToOpData(valuesDict)
                self.__data.append(opData)
            line = file.readline()
        file.close()

    def saveInFile(self, filepath: str, generateDebugFile: bool):
        """
            Save all the OPD data in a TXT file.
            :param filepath: Path to the output file.
            :param generateDebugFile: Set to True if you want to generate the "opd_debug.txt" file in the same
                directory than "filepath".
        """
        # Create the OPD file.
        fOpd = create_result_file(filepath)
        fOpd.write(
            "#! Note: Asym = Asymmetric, Func = Functional, InFu = InverseFunctional, Irre = Irreflexive, Refl = "
            "Reflexive, Symm = Symmetric, Tran = Transitive, DoIns = Nb Domain Instances, RaIns = Nb Range Instances\n")
        fOpd.write("\n")
        fOpd.write("#! Columns: \n")
        fOpd.write(OPD.COLUMNS_NAMES_FORMAT % OPD.COLUMNS_NAMES)
        fOpd.write("\n")
        for opData in self.__data:
            lineData = _opDataToValues(opData)
            fOpd.write(OPD.LINE_FORMAT % (
                lineData["File"], lineData["ObjectProperty"], lineData["Domains"], lineData["Ranges"],
                lineData["InverseOf"], lineData["SubPropertyOf"], lineData["DoIns"], lineData["RaIns"],
                int(lineData["Asym?"]), int(lineData["Func?"]), int(lineData["InFu?"]), int(lineData["Irre?"]),
                int(lineData["Refl?"]), int(lineData["Symm?"]), int(lineData["Tran?"]),
                lineData["OpIRI"], lineData["DomainsIRIs"], lineData["RangesIRIs"], lineData["InverseOfIRI"],
                lineData["SubPropertyOfIRIs"]
            ))
        fOpd.close()

        if generateDebugFile:
            # Generate "opd_debug.txt" file for debugging
            filepathDebug = os.path.join(os.path.dirname(filepath), "opd_debug.txt")
            fDebug = create_result_file(filepathDebug)
            fDebug.write("# Note: If the file is loaded with Rdflib, then it will not try to load with Owlready2.\n\n")
            fDebug.write(OPD.LINE_FORMAT_DEBUG % (
                "File", "Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbOp", "OpUnreada.", "MustKeep"))
            fDebug.write("\n")

            for filename in self.__filenames:
                time_str = "%-9.2f" % self.__debugData["Time"][filename]
                fDebug.write(OPD.LINE_FORMAT_DEBUG % (
                    filename, self.__debugData["Rdflib?"][filename], self.__debugData["Owlready?"][filename],
                    self.__debugData["Loaded?"][filename], self.__debugData["NbErrors"][filename], time_str,
                    self.__debugData["NbOp"][filename], self.__debugData["OpUnreadable"][filename],
                    self.__debugData["MustKeep"][filename]))

            fDebug.write("\n")
            time_str = "%-9.2f" % sum(self.__debugData["Time"].values())
            fDebug.write(OPD.LINE_FORMAT_DEBUG % (
                "Total", sum(self.__debugData["Rdflib?"].values()), sum(self.__debugData["Owlready?"].values()),
                sum(self.__debugData["Loaded?"].values()), sum(self.__debugData["NbErrors"].values()), time_str,
                sum(self.__debugData["NbOp"].values()), sum(self.__debugData["OpUnreadable"].values()),
                sum(self.__debugData["MustKeep"].values())))
            fDebug.write("\n")
            fDebug.write("Nb of files: %d\n" % len(self.__filenames))
            fDebug.close()

    def filter(self, fctFilter):
        """
            Remove all op data that does not pass the filter.
            :param fctFilter: Return true if you want to keep the op data in parameter.
        """
        newData = []
        for values in self.__data:
            if fctFilter(values):
                newData.append(values)
        self.__data = newData

    def clear(self):
        """
            Clear the OPD data.
        """
        self.__data = []
        self.__debugData = {name: {} for name in OPD.COLUMNS_NAMES_DEBUG}
        self.__version = "Unknown"
        self.__srcpath = ""
        self.__filenames = []

    def getData(self) -> list:
        """
            Get the data of the OPD.
            :return: list of OpData objects.
        """
        return self.__data

    def getOpNames(self, filterDuplicates: bool = False) -> list:
        opNames = []
        for opData in self.getData():
            opNames.append(opData.getName())
        if filterDuplicates:
            return rem_duplicates(opNames)
        else:
            return opNames

    def getOpNamesSplit(self, keepEmptyLists: bool, filterDomain: bool = False, filterRange: bool = False,
                        filterSubWords: list = None, filterDuplicates: bool = False) -> list:
        opNamesSplit = []
        for opData in self.getData():
            splitted = opData.getNameSplit(
                filterDomain=filterDomain, filterRange=filterRange, filterSubWords=filterSubWords)
            if len(splitted) > 0 or keepEmptyLists:
                opNamesSplit.append(splitted)
        if filterDuplicates:
            return rem_duplicates(opNamesSplit)
        else:
            return opNamesSplit

    def getSize(self) -> int:
        """
            Equivalent to "len(opd.getData())".
            :return: the number of OP stored in OPD.
        """
        return len(self.__data)

    def getSrcpath(self) -> str:
        return self.__srcpath

    def getVersion(self) -> str:
        return self.__version

    def __eq__(self, other) -> bool:
        return self.__data == other.__data
