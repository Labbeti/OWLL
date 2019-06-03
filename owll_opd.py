from ontology.Ontology import Ontology
from time import time
from util import *

import re


# The OBO Foundry contains a lot of op names like "BFO_0000050", there are useless for semantic learning.
# ex unreadable: BFO_0000050, RO_000050, APOLLO_SV_00001, NCIT_R100
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
    values = values[1:len(values)-1]
    values = [value.strip() for value in values]
    return values


# Generate the Object Property Database (OPD) in "results/opd/opd.txt".
def gen_opd(args: str = ""):
    # Parameters
    dirpath = "data/ontologies"
    filepathResults = "results/opd/opd.txt"
    filepathMeta = "results/opd/opd_meta.txt"

    # Global values for results format
    metaNames = ["Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbTriples", "OpUnreadable", "MustKeep"]
    meta = {name: {} for name in metaNames}
    line_meta_format = "%-40s" + (" %-10s" * len(metaNames)) + "\n"
    column_names = ("File", "ObjectProperty", "Domain", "Range", "Asym?", "Func?", "InFu?", "Irre?", "Refl?", "Symm?",
                    "Tran?", "Inst", "InverseOf", "SubPropertyOf")
    column_format = ("| %-35s " * 4) + ("| %-5s " * 8) + ("| %-35s " * 2) + "| \n"
    line_format = ("| %-35s " * 4) + ("| %-5d " * 8) + ("| %-35s " * 2) + "| \n"

    # Get the filenames of the ontologies
    filenames = get_filenames(dirpath)

    # Create the OPD file with a specific header
    out = open(filepathResults, "w", encoding='utf-8', errors='ignore')
    out.write("#! Version: %s\n" % get_time())
    out.write("#! Note: Asym = Asymmetric, Func = Functional, InFu = InverseFunctional, Irre = Irreflexive, "
              "Refl = Reflexive, Symm = Symmetric, Tran = Transitive, Inst = Nb Instances\n")
    out.write("#!\n")
    out.write("#! Columns: \n")
    out.write(column_format % column_names)
    out.write("\n")

    i = 1
    for filename in filenames:
        # Read the ontology and save data in opd
        start = time()
        prt("Load of \"%s\"... (%d/%d)" % (filename, i, len(filenames)))
        filepath = os.path.join(dirpath, filename)
        ontology = Ontology(filepath)

        if ontology.isLoaded():
            prt("Load of \"%s\" is successfull (RL=%d,OR=%d) (%d/%d)" % (filename, ontology.isLoadedWithRL(),
                                                                         ontology.isLoadedWithOR2(), i, len(filenames)))
            triples = ontology.getOWLTriples()
            for (domainUri, opUri, rangeUri) in triples:
                domainName = ontology.getName(domainUri)
                opName = ontology.getName(opUri)
                rangeName = ontology.getName(rangeUri)
                opChars = ontology.getOPCharacteristics(opUri)
                invName = ontology.getName(opChars.inverseOf)
                parentNames = [ontology.getName(propUri) for propUri in opChars.subPropertyOf]
                subPropOf = ",".join(parentNames) if len(parentNames) > 0 else \
                    Config.OPD_DEFAULT.SUBPROPERTY_OF
                out.write(line_format %
                          (filename, opName, domainName, rangeName, opChars.isAsymmetric,
                           opChars.isFunctional, opChars.isInverseFunctional, opChars.isIrreflexive,
                           opChars.isReflexive, opChars.isSymmetric, opChars.isTransitive, opChars.nbInstances,
                           invName, subPropOf))
        else:
            triples = []
            prt("Load of \"%s\" has failed (%d/%d)" % (filename, i, len(filenames)))
        end = time()

        # Get some information for "opd_meta"
        nbUnreadable = __count_unreadables(triples)
        meta["Rdflib?"][filename] = ontology.isLoadedWithRL()
        meta["Owlready?"][filename] = ontology.isLoadedWithOR2()
        meta["Loaded?"][filename] = ontology.isLoaded()
        meta["NbErrors"][filename] = ontology.getNbErrors()
        meta["Time"][filename] = end - start
        meta["NbTriples"][filename] = len(triples)
        meta["OpUnreadable"][filename] = nbUnreadable
        meta["MustKeep"][filename] = ontology.isLoaded() and nbUnreadable == 0 and len(triples) > 0
        i += 1

    out.close()

    # Generate "opd_meta.txt" file for debugging
    fmeta = open(filepathMeta, "w", encoding='utf-8', errors='ignore')
    fmeta.write("#! Version: %s\n" % get_time())
    fmeta.write(line_meta_format % ("File", "Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbTriples",
                                    "OpUnreada.", "MustKeep"))
    fmeta.write("\n")

    for filename in filenames:
        time_str = "%-9.2f" % meta["Time"][filename]
        fmeta.write(line_meta_format % (filename, meta["Rdflib?"][filename], meta["Owlready?"][filename],
                                        meta["Loaded?"][filename], meta["NbErrors"][filename], time_str,
                                        meta["NbTriples"][filename], meta["OpUnreadable"][filename],
                                        meta["MustKeep"][filename]))
    fmeta.write("\n")
    time_str = "%-9.2f" % sum(meta["Time"].values())
    fmeta.write(line_meta_format % ("Total", sum(meta["Rdflib?"].values()), sum(meta["Owlready?"].values()),
                                    sum(meta["Loaded?"].values()), sum(meta["NbErrors"].values()), time_str,
                                    sum(meta["NbTriples"].values()), sum(meta["OpUnreadable"].values()),
                                    sum(meta["MustKeep"].values())))
    fmeta.write("\n")
    fmeta.write("Nb of files: %d\n" % len(filenames))
    fmeta.close()

    prt("")
    prt("Files \"%s\" and \"%s\" saved. " % (filepathResults, filepathMeta))


# Read the data contained in a OPD file.
# Returns (data, version, columns names)
def read_opd(filepath_opd: str) -> (list, str, list):
    fopd = open(filepath_opd, "r", encoding='utf-8')

    # Read Header
    versionOpd = "Unknown"
    columnsNames = []
    line = fopd.readline()
    while line and line.startswith("#!"):
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
                raise Exception("Incorrect OPD \"%s\"" % filepath_opd)

            valuesDict = {columnsNames[i]: values[i] for i in range(len(values))}
            data.append(valuesDict)
        line = fopd.readline()

    fopd.close()
    return data, versionOpd, columnsNames


if __name__ == "__main__":
    # gen_opd()
    pass
