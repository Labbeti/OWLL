from Config import *
from Ontology import Ontology
from time import strftime
from time import time
from utils import *

import re


def get_time() -> str:
    return strftime("%d/%m/%Y_%H:%M:%S")


# The OBO Foundry contains a lot of op names like "BFO_0000050", there are useless for semantic learning.
# Pattern considered as unreadable: "[A-Z_]+_[0-9]+"
def is_unreadable(name: str) -> bool:
    return re.match("[A-Z_]+_[0-9]+", name) is not None


def count_unreadables(triples: list) -> int:
    count = 0
    for _, p, _ in triples:
        if is_unreadable(p):
            count += 1
    return count


def gen_object_properties_database():
    dirpath = "data/ontologies"
    filepath_results = "results/object_properties_database.txt"
    filepath_meta = "results/meta_results_opd.txt"

    filenames = get_filenames(dirpath)[160:200]
    stats_names = ["Owlready?", "Rdflib?", "NbErrors", "Time", "NbTriples", "OpUnreadable"]
    stats = {name: {} for name in stats_names}
    out = open(filepath_results, "w", encoding='utf-8', errors='ignore')
    out.write("#! Version: %s\n" % get_time())
    out.write("%-30s %-30s %-30s %-30s\n\n" % ("#Object property", "Domain", "Range", "File"))

    i = 1
    for filename in filenames:
        start = time()
        prt("LOADING %s... (%d/%d)" % (filename, i, len(filenames)))
        filepath = join(dirpath, filename)
        ontology = Ontology(filepath)

        triples = []
        if ontology.is_loaded():
            prt("Load of %s is successfull (%d/%d)" % (filename, i, len(filenames)))
            triples = ontology.get_op_triples()
            for op_domain, op, op_range in triples:
                out.write("%-30s %-30s %-30s %-30s\n" % (op, op_domain, op_range, filename))
        else:
            prt("Load of %s has failed (%d/%d)" % (filename, i, len(filenames)))
        end = time()

        stats["Owlready?"][filename] = ontology.is_loaded_with_owlready2()
        stats["Rdflib?"][filename] = ontology.is_loaded_with_rdflib()
        stats["NbErrors"][filename] = ontology.get_nb_errors()
        stats["Time"][filename] = end - start
        stats["NbTriples"][filename] = len(triples)
        stats["OpUnreadable"][filename] = count_unreadables(triples)
        i += 1

    meta = open(filepath_meta, "w", encoding='utf-8', errors='ignore')
    line_format = "%-30s %-10s %-10s %-10s %-10s %-10s %-10s\n"
    meta.write(line_format % ("File", "Owlready?", "Rdflib?", "NbErrors", "Time", "NbTriples", "OpUnreadable"))
    meta.write("\n")

    for filename in filenames:
        time_str = "%-9.2f" % stats["Time"][filename]
        meta.write(line_format % (filename, stats["Owlready?"][filename], stats["Rdflib?"][filename],
                                  stats["NbErrors"][filename], time_str, stats["NbTriples"][filename],
                                  stats["OpUnreadable"][filename]))
    meta.write("\n")
    time_str = "%-9.2f" % sum(stats["Time"].values())
    meta.write(line_format % ("Total", sum(stats["Owlready?"].values()), sum(stats["Rdflib?"].values()),
                              sum(stats["NbErrors"].values()), time_str,
                              sum(stats["NbTriples"].values()), sum(stats["OpUnreadable"].values())))
    meta.write("\n")
    meta.write("Nb of files: %d\n" % len(filenames))

    out.close()
    meta.close()
    prt("")
    prt("Files \"%s\" and \"%s\" saved. " % (filepath_results, filepath_meta))


def classify_names():
    filepath_opd = "results/object_properties_database.txt"
    filepath_words = "results/words.txt"

    opd = open(filepath_opd, "r", encoding='utf-8', errors='ignore')
    results = {word_type: {} for word_type in ["Prefix", "Suffix", "Inside"]}
    version_opd = "Unknown"

    nb_op = 0
    for line in opd:
        if line != "\n" and line[0] != "#":
            values = rem_empty(line.split(" "))
            values.pop()  # Remove '\n' at the end of the list
            op_name = values[0]
            words_name = split_name(op_name)
            words_name = [word.lower() for word in words_name]

            words_found = [word_searched for word_searched in WORDS_SEARCHED if word_searched in words_name]
            words_type = [("Prefix" if word == words_name[0] else
                           "Suffix" if word == words_name[-1] else
                           "Inside") for word in words_found]

            for i in range(len(words_found)):
                word_found = words_found[i]
                word_type = words_type[i]
                if word_found not in results[word_type].keys():
                    results[word_type][word_found] = []
                results[word_type][word_found].append(op_name)
            nb_op += 1
        elif line.startswith("#!"):
            version_opd = line.split(" ")[2].replace("\n", "")
    opd.close()

    out = open(filepath_words, "w", encoding='utf-8', errors='ignore')
    out.write("#! Version: %s\n" % get_time())
    out.write("# This file has been generated with the file \"%s\" (version %s)\n" % (filepath_opd, version_opd))
    out.write("# Words searched are : %s\n" % str(WORDS_SEARCHED))
    out.write("\n")

    for word_type, _ in results.items():
        for word_found, words in results[word_type].items():
            proportion = 100 * len(words) / nb_op
            out.write("Word \"%s\" (%s) %d/%d (%.2f%%)\n" % (word_found, word_type, len(words), nb_op, proportion))
            for word in words:
                out.write("%s, " % word)
            out.write("\n\n")

    out.close()


def filter_opd():
    filepath_opd = "results/object_properties_database.txt"
    filepath_opd_filtered = "results/opd_2.txt"

    buffer = ""
    opd = open(filepath_opd, "r", encoding='utf-8', errors='ignore')
    doespassfilter = lambda pvalues: not is_unreadable(pvalues[0])
    version_opd = "Unknown"

    for line in opd:
        if line[0] != "#":
            values = rem_empty(line.split(" "))
            values.pop()  # Remove '\n' at the end of the list
            op_name = values[0]
            # words = split_name(op_name)

            if doespassfilter(values):
                buffer += line
        elif line.startswith("#!"):
            version_opd = line.split(" ")[1]

    out = open(filepath_opd_filtered, "w", encoding='utf-8', errors='ignore')
    out.write("#! Version: %s\n" % get_time())
    out.write("# This file has been generated with the file \"%s\" (version %s)\n" % (filepath_opd, version_opd))
    out.write("# Words searched are : %s\n" % str(Config.LINK_WORDS))
    out.write(buffer)
    out.close()
