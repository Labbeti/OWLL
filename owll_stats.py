from ontology.LoadType import LoadType
from ontology.Ontology import Ontology
from ontology.Ontology import RdflibOntology
from time import time
from utils import *

import re


OP_INDEX: int = 1


# The OBO Foundry contains a lot of op names like "BFO_0000050", there are useless for semantic learning.
# ex unreadable: BFO_0000050, RO_000050, APOLLO_SV_00001, NCIT_R100
def is_unreadable(name: str) -> bool:
    return re.match("[A-Z_]+_[A-Z0-9]+", name) is not None


def count_unreadables(triples: list) -> int:
    count = 0
    for _, p, _ in triples:
        if is_unreadable(p):
            count += 1
    return count


def can_pass_filter(values: list) -> bool:
    return not is_unreadable(values[OP_INDEX])


def get_opd(filepath_opd: str) -> (list, str):
    fopd = open(filepath_opd, "r", encoding='utf-8', errors='ignore')
    version_opd = "Unknown"
    data = []
    for line in fopd:
        if line != "\n" and not line.startswith("#"):
            values = rem_empty(line.split(" "))
            values.pop()  # Remove '\n' at the end of the list
            data.append(values)
        elif line.startswith("#!"):
            version_opd = line.split(" ")[2].replace("\n", "")
    fopd.close()
    return data, version_opd


# Generate the Object Property Database (OPD) in opd.txt
def gen_opd():
    dirpath = "data/ontologies"
    filepath_results = "results/stats/opd.txt"
    filepath_meta = "results/stats/opd_meta.txt"

    filenames = get_filenames(dirpath)
    stats_names = ["Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbTriples", "OpUnreadable", "MustKeep"]
    stats = {name: {} for name in stats_names}
    out = open(filepath_results, "w", encoding='utf-8', errors='ignore')
    out.write("#! Version: %s\n" % get_time())
    out.write("# Note: Asym = Asymmetric, Func = Functional, InFu = InverseFunctional, Irre = Irreflexive, "
              "Refl = Reflexive, Symm = Symmetric, Tran = Transitive, Inst = Nb Instances, InOf = Inverse Of\n\n")
    column_names = ("#File", "Object property", "Domain", "Range", "Asym?", "Func?", "InFu?", "Irre?", "Refl?",
                    "Symm?", "Tran?", "Inst", "InOf")
    line_format = "%-30s %-30s %-30s %-30s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s\n"
    out.write(line_format % column_names)
    out.write("\n")

    i = 1
    for filename in filenames:
        start = time()
        prt("Load of \"%s\"... (%d/%d)" % (filename, i, len(filenames)))
        filepath = join(dirpath, filename)
        ontology = Ontology(filepath)

        if ontology.isLoaded():
            prt("Load of \"%s\" is successfull (%d/%d)" % (filename, i, len(filenames)))
            triples = ontology.getOWLTriples()
            for (domainUri, opUri, rangeUri) in triples:
                domainName = ontology.getName(domainUri)
                opName = ontology.getName(opUri)
                rangeName = ontology.getName(rangeUri)
                opChars = ontology.getOPCharacteristics(opUri)
                invName = ontology.getName(opChars.inverseOf)
                out.write("%-30s %-30s %-30s %-30s %-5d %-5d %-5d %-5d %-5d %-5d %-5d %-5d %-30s\n" %
                          (filename, opName, domainName, rangeName, opChars.isAsymmetric, opChars.isFunctional,
                           opChars.isInverseFunctional, opChars.isIrreflexive, opChars.isReflexive, opChars.isSymmetric,
                           opChars.isTransitive, opChars.nbInstances, invName))
        else:
            triples = []
            prt("Load of \"%s\" has failed (%d/%d)" % (filename, i, len(filenames)))
        end = time()

        nb_unreadable = count_unreadables(triples)
        stats["Rdflib?"][filename] = ontology.isLoadedWithRL()
        stats["Owlready?"][filename] = ontology.isLoadedWithOR2()
        stats["Loaded?"][filename] = ontology.isLoaded()
        stats["NbErrors"][filename] = ontology.getNbErrors()
        stats["Time"][filename] = end - start
        stats["NbTriples"][filename] = len(triples)
        stats["OpUnreadable"][filename] = nb_unreadable
        stats["MustKeep"][filename] = ontology.isLoaded() and nb_unreadable == 0 and len(triples) > 0
        i += 1

    meta = open(filepath_meta, "w", encoding='utf-8', errors='ignore')
    line_format = "%-40s" + (" %-10s" * len(stats)) + "\n"
    meta.write("#! Version: %s\n" % get_time())
    meta.write(line_format % ("File", "Rdflib?", "Owlready?", "Loaded?", "NbErrors", "Time", "NbTriples", "OpUnreada.",
                              "MustKeep"))
    meta.write("\n")

    for filename in filenames:
        time_str = "%-9.2f" % stats["Time"][filename]
        meta.write(line_format % (filename, stats["Rdflib?"][filename], stats["Owlready?"][filename],
                                  stats["Loaded?"][filename], stats["NbErrors"][filename], time_str,
                                  stats["NbTriples"][filename], stats["OpUnreadable"][filename],
                                  stats["MustKeep"][filename]))
    meta.write("\n")
    time_str = "%-9.2f" % sum(stats["Time"].values())
    meta.write(line_format % ("Total", sum(stats["Rdflib?"].values()), sum(stats["Owlready?"].values()),
                              sum(stats["Loaded?"].values()), sum(stats["NbErrors"].values()), time_str,
                              sum(stats["NbTriples"].values()), sum(stats["OpUnreadable"].values()),
                              sum(stats["MustKeep"].values())))
    meta.write("\n")
    meta.write("Nb of files: %d\n" % len(filenames))

    out.close()
    meta.close()
    prt("")
    prt("Files \"%s\" and \"%s\" saved. " % (filepath_results, filepath_meta))


# Generate some stats about connect word (Config.CONNECT_WORDS)
def connect_words_stats():
    filepath_opd = "results/stats/opd.txt"
    filepath_words = "results/stats/connect_words_stats.txt"

    results = {word_type: {} for word_type in ["Prefix", "Suffix", "Inside"]}

    data, version_opd = get_opd(filepath_opd)
    for values in data:
        op_name = values[OP_INDEX]
        words_name = split_name(op_name)
        words_name = [word.lower() for word in words_name]

        conn_words_found = [conn_word for conn_word in Config.CONNECT_WORDS if conn_word in words_name]
        conn_words_type = [("Prefix" if word == words_name[0] else
                            "Suffix" if word == words_name[-1] else
                            "Inside") for word in conn_words_found]

        for i in range(len(conn_words_found)):
            conn_word_found = conn_words_found[i]
            conn_word_type = conn_words_type[i]
            if conn_word_found not in results[conn_word_type].keys():
                results[conn_word_type][conn_word_found] = []
            results[conn_word_type][conn_word_found].append(op_name)

    out = open(filepath_words, "w", encoding='utf-8', errors='ignore')
    out.write("#! Version: %s\n" % get_time())
    out.write("# This file has been generated with the file \"%s\" (version %s)\n" % (filepath_opd, version_opd))
    out.write("# Words searched are : %s\n" % str(Config.CONNECT_WORDS))
    out.write("\n")

    results_sort = []
    for word_type, _ in results.items():
        for conn_word_found, words in results[word_type].items():
            proportion = 100 * len(words) / len(data)
            results_sort.append((proportion, word_type, conn_word_found, words))

    results_sort.sort(key=lambda x: x[0], reverse=True)
    for (proportion, word_type, conn_word_found, words) in results_sort:
        out.write("%s: Word \"%s\" %d/%d (%.2f%%)\n" % (word_type, conn_word_found, len(words), len(data),
                                                        proportion))
        for word in words:
            out.write("%s, " % word)
        out.write("\n\n")

    out.close()


# Generate a opd filtered (UNUSED)
def filter_opd():
    filepath_opd = "results/stats/opd.txt"
    filepath_opd_filtered = "results/stats/opd_2.txt"

    buffer = ""
    data, version_opd = get_opd(filepath_opd)

    for values in data:
        if can_pass_filter(values):
            buffer += "%-30s %-30s %-30s %-30s\n" % values

    out = open(filepath_opd_filtered, "w", encoding='utf-8', errors='ignore')
    out.write("#! Version: %s\n" % get_time())
    out.write("# This file has been generated with the file \"%s\" (version %s)\n" % (filepath_opd, version_opd))
    out.write("# Words searched are : %s\n" % str(Config.CONNECT_WORDS))
    out.write(buffer)
    out.close()


# Generate a partition of op names
def extract_words():
    filepath_opd = "results/stats/opd.txt"
    filepath_meta = "results/stats/root_words_meta.txt"
    filepath_results = "results/stats/root_words.txt"

    root_names = []
    root_words = set()
    empty_names = []
    other_names = []
    data, version_opd = get_opd(filepath_opd)

    for values in data:
        op_name = values[OP_INDEX]
        words_name = split_name(op_name)

        # Rem Connect Words
        words_without_cw = [word for word in words_name if word.lower() not in Config.CONNECT_WORDS]
        op_domain = values[1]
        op_range = values[2]
        # Rem Connect Words, Domain and Range
        words_without_cwdr = [word for word in words_without_cw
                              if word.lower() != op_domain.lower() and word.lower() != op_range.lower()]

        if len(words_without_cwdr) == 1:
            root_names.append(op_name)
            root_words.add(words_without_cwdr[0].lower())
        elif len(words_without_cwdr) == 0:
            empty_names.append(op_name)
        else:
            other_names.append(op_name)

    out = open(filepath_meta, "w", encoding="utf-8")
    out.write("#! Version: %s\n" % get_time())
    out.write("# This file has been generated with the file \"%s\" (version %s)\n" % (filepath_opd, version_opd))
    out.write("# Words searched are : %s\n\n" % str(Config.CONNECT_WORDS))

    proportion = 100 * len(root_names) / len(data)
    out.write("Root words %d/%d (%.2f%%), (unique = %d)\n" % (len(root_names), len(data), proportion, len(root_words)))
    i = 0
    for word in root_names:
        out.write("%s, " % word)
        i += 1
        if i % 100 == 0:
            out.write("\n")
    out.write("\n\n")

    proportion = 100 * len(empty_names) / len(data)
    out.write("Empty words %d/%d (%.2f%%)\n" % (len(empty_names), len(data), proportion))
    i = 0
    for word in empty_names:
        out.write("%s, " % word)
        i += 1
        if i % 100 == 0:
            out.write("\n")
    out.write("\n\n")

    proportion = 100 * len(other_names) / len(data)
    out.write("Other words %d/%d (%.2f%%)\n" % (len(other_names), len(data), proportion))
    i = 0
    for word in other_names:
        out.write("%s, " % word)
        i += 1
        if i % 100 == 0:
            out.write("\n")
    out.write("\n")
    out.close()

    out = open(filepath_results, "w", encoding="utf-8")
    out.write("#! Version: %s\n" % get_time())
    out.write("# This file has been generated with the file \"%s\" (version %s)\n" % (filepath_opd, version_opd))
    out.write("# Root words: \n")
    for word in root_words:
        out.write("%s\n" % word)
    out.close()


if __name__ == "__main__":
    #gen_opd()
    connect_words_stats()
    extract_words()
