from file_io import create_result_file
from ontology.Ontology import Ontology
from time import time
from util import *

import re
import sys


# The OBO Foundry contains a lot of op names like "BFO_0000050", there are useless for semantic learning.
# ex: BFO_0000050, RO_000050, APOLLO_SV_00001, NCIT_R100
def __is_unreadable(name: str) -> bool:
    return re.match("[A-Z_]+_[A-Z0-9]+", name) is not None


def __count_unreadables(triples: list) -> int:
    count = 0
    for _, p, _ in triples:
        if __is_unreadable(p):
            count += 1
    return count


def __get_values(line: str) -> list:
    values = line.split("|")
    # Values: ["", "File...", "Op...", ..., "SubPropOf...", "\n"]
    values = values[1:len(values) - 1]
    values = [value.strip() for value in values]
    return values


# Generate the Object Property Database (OPD) in "results/opd/opd.txt".
def gen_opd(args: list = None) -> int:
    # Initializing values...
    if args is not None and len(args) > 2:
        prt("Error: Unexpected number of arguments: %d" % len(args))
        return 1

    dirpathOnto, filepathOpd = get_args(args, [Consts.Path.Dir.ONTOLOGIES, Consts.Path.File.Result.OPD])
    if not os.path.isdir(dirpathOnto):
        prt("Error: %s must be a directory." % dirpathOnto)
        return 2
    if not os.path.isfile(filepathOpd):
        prt("Error: %s must be a file." % filepathOpd)
        return 3

    prt("Search ontologies in \"%s\" and save results in \"%s\"" % (dirpathOnto, filepathOpd))
    filepathOpdMeta = os.path.join(os.path.dirname(filepathOpd), "opd_debug.txt")

    columnsNames = ("Filename", "ObjectProperty", "Domain", "Range", "Asym?", "Func?", "InFu?", "Irre?", "Refl?",
                    "Symm?", "Tran?", "DoIns", "RaIns", "InverseOf", "SubPropertyOf")
    columnsNamesFormat = ("| %-35s " * 4) + ("| %-5s " * 9) + ("| %-35s " * 2) + "| \n"
    lineFormat = ("| %-35s " * 4) + ("| %-5d " * 9) + ("| %-35s " * 2) + "| \n"

    debugColumnsNames = ["Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbTriples", "OpUnreadable", "MustKeep"]
    lineDebugFormat = "%-40s" + (" %-10s" * len(debugColumnsNames)) + "\n"
    debugStats = {name: {} for name in debugColumnsNames}

    # Get the filenames of the ontologies
    filenames = get_filenames(dirpathOnto)

    # Create the OPD file
    fOut = create_result_file(filepathOpd)
    fOut.write("#! Note: Asym = Asymmetric, Func = Functional, InFu = InverseFunctional, Irre = Irreflexive, "
               "Refl = Reflexive, Symm = Symmetric, Tran = Transitive, DoIns = Nb Domain Instances, RaIns = Nb "
               "Range Instances \n")
    fOut.write("\n")
    fOut.write("#! Columns: \n")
    fOut.write(columnsNamesFormat % columnsNames)
    fOut.write("\n")

    # TODO : put paths to Consts
    prt("Reading english words...")
    fEnglishWords = open(Consts.Path.File.ENGLISH_WORDS, "r", encoding="utf-8")
    englishWords = set()
    for line in fEnglishWords:
        englishWords.add(line.replace("\n", "").lower())
    fEnglishWords.close()
    fUnusedWords = create_result_file(Consts.Path.File.Result.UNUSED_WORDS)
    fUnusedWords.write("# This file contains non-english words found when creating OPD.\n\n")
    fUnusedWords.write("%-30s %-40s %-40s\n\n" % ("Word", "ObjectProperty", "Filename"))

    # Read the list of ontologies
    i = 1
    for filename in filenames:
        # Read the ontology and save data in opd
        start = time()
        prt("Load of \"%s\"... (%d/%d)" % (filename, i, len(filenames)))
        filepath = os.path.join(dirpathOnto, filename)
        ontology = Ontology(filepath)

        if ontology.isLoaded():
            prt("Load of \"%s\" is successfull (RL=%d,OR=%d) (%d/%d)" % (
                filename, ontology.isLoadedWithRL(), ontology.isLoadedWithOR2(), i, len(filenames)))

            for opName in ontology.getOpNames():
                opNameSplit = str_list_lower(split_op_name(opName))
                for word in opNameSplit:
                    if word not in englishWords:
                        fUnusedWords.write("%-30s %-40s %-40s\n" % (word, opName, filepath))

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
                subPropOf = ",".join(parentNames) if len(parentNames) > 0 else \
                    Consts.DefaultOpdValues.SUBPROPERTY_OF

                fOut.write(lineFormat % (
                    filename, opName, domainName, rangeName, opProps.isAsymmetric, opProps.isFunctional,
                    opProps.isInverseFunctional, opProps.isIrreflexive, opProps.isReflexive, opProps.isSymmetric,
                    opProps.isTransitive, domaimProps.nbInstances, rangeProps.nbInstances, invName, subPropOf))
        else:
            triples = []
            prt("Load of \"%s\" has failed (%d/%d)" % (filename, i, len(filenames)))
        end = time()

        # Get some information for "opd_debug"
        nbUnreadable = __count_unreadables(triples)
        debugStats["Rdflib?"][filename] = ontology.isLoadedWithRL()
        debugStats["Owlready?"][filename] = ontology.isLoadedWithOR2()
        debugStats["Loaded?"][filename] = ontology.isLoaded()
        debugStats["NbErrors"][filename] = ontology.getNbErrors()
        debugStats["Time"][filename] = end - start
        debugStats["NbTriples"][filename] = len(triples)
        debugStats["OpUnreadable"][filename] = nbUnreadable
        debugStats["MustKeep"][filename] = ontology.isLoaded() and nbUnreadable == 0 and len(triples) > 0
        i += 1

    fOut.close()
    fUnusedWords.close()

    # Generate "opd_debug.txt" file for debugging
    fDebugOut = create_result_file(filepathOpdMeta)
    fDebugOut.write("# Note: If the file is loaded with Rdflib, then it will not try to load with Owlready2.\n\n")
    fDebugOut.write(lineDebugFormat % (
        "File", "Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbTriples", "OpUnreada.", "MustKeep"))
    fDebugOut.write("\n")

    for filename in filenames:
        time_str = "%-9.2f" % debugStats["Time"][filename]
        fDebugOut.write(lineDebugFormat % (
            filename, debugStats["Rdflib?"][filename], debugStats["Owlready?"][filename],
            debugStats["Loaded?"][filename], debugStats["NbErrors"][filename], time_str,
            debugStats["NbTriples"][filename], debugStats["OpUnreadable"][filename], debugStats["MustKeep"][filename]))
    fDebugOut.write("\n")
    time_str = "%-9.2f" % sum(debugStats["Time"].values())
    fDebugOut.write(lineDebugFormat % (
        "Total", sum(debugStats["Rdflib?"].values()), sum(debugStats["Owlready?"].values()),
        sum(debugStats["Loaded?"].values()), sum(debugStats["NbErrors"].values()), time_str,
        sum(debugStats["NbTriples"].values()), sum(debugStats["OpUnreadable"].values()),
        sum(debugStats["MustKeep"].values())))
    fDebugOut.write("\n")
    fDebugOut.write("Nb of files: %d\n" % len(filenames))
    fDebugOut.close()

    prt("")
    prt("Files \"%s\" and \"%s\" saved. " % (filepathOpd, filepathOpdMeta))
    return 0


# Read the data contained in a OPD file.
# Returns (data: list of dict, version: str, columns names: list of str)
def read_opd(filepathOPD: str) -> (list, str, list):
    fopd = open(filepathOPD, "r", encoding='utf-8')

    # Read Header
    versionOpd = "Unknown"
    columnsNames = []
    line = fopd.readline()
    while line and (line.startswith("#!") or line == "\n"):
        if line.startswith("#! Version: "):
            versionOpd = line.split(" ")[2].replace("\n", "")
        elif line.startswith("#! Columns: "):
            line = fopd.readline()
            values = __get_values(line)
            # values => "File | ObjectProperty | ... |\n"
            columnsNames = values
        line = fopd.readline()

    if len(columnsNames) == 0:
        raise Exception("Incorrect OPD Header. Missing columns names line.")
    elif versionOpd == "Unknown":
        raise Exception("Incorrect OPD Header. Missing version line.")

    # Read data
    data = []
    while line:
        if line != "\n" and not line.startswith("#"):
            values = __get_values(line)
            if values[-1] == "\n":
                values.pop()  # Remove '\n' at the end of the list
            if len(columnsNames) != len(values):
                raise Exception("Incorrect OPD \"%s\"" % filepathOPD)

            valuesDict = {columnsNames[i]: values[i] for i in range(len(values))}
            data.append(valuesDict)
        line = fopd.readline()

    fopd.close()
    return data, versionOpd, columnsNames


if __name__ == "__main__":
    commandArgs = sys.argv[1:]
    gen_opd(commandArgs)
