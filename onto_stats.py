
from Ontology import Ontology
from time import time
from utils import *


def gen_object_properties_database():
    dirpath = "data/ontologies"
    filepath_results = "results/object_properties_database.txt"
    filepath_meta = "results/meta_results_opd.txt"

    stats_names = ["Owlready2?", "Rdflib?", "NbErrors", "Time", "NbTriples"]
    stats = {name: {} for name in stats_names}
    filenames = get_filenames(dirpath)
    out = open(filepath_results, "w", encoding='utf-8', errors='ignore')
    out.write("%-30s %-30s %-30s %-30s\n\n" % ("Object property", "Domain", "Range", "File"))

    i = 1
    for filename in filenames:
        start = time()
        print("§ LOADING %s... (%d/%d)" % (filename, i, len(filenames)))
        filepath = join(dirpath, filename)
        ontology = Ontology(filepath)

        triples = []
        if ontology.is_loaded():
            print("§ Load of %s is successfull (%d/%d)" % (filename, i, len(filenames)))
            triples = ontology.get_owl_triples()
            for op_domain, op, op_range in triples:
                out.write("%-30s %-30s %-30s %-30s\n" % (op, op_domain, op_range, filename))
        else:
            print("§ Load of %s has failed (%d/%d)" % (filename, i, len(filenames)))
        end = time()

        stats["Owlready2?"][filename] = ontology.is_loaded_with_owlready2()
        stats["Rdflib?"][filename] = ontology.is_loaded_with_rdflib()
        stats["NbErrors"][filename] = ontology.get_nb_errors()
        stats["Time"][filename] = end - start
        stats["NbTriples"][filename] = len(triples)
        i += 1

    meta = open(filepath_meta, "w", encoding='utf-8', errors='ignore')
    meta.write("%-30s %-11s %-9s %-9s %-8s %-10s\n\n" % ("File", "Owlready2?", "Rdflib?", "NbErrors", "Time",
                                                         "NbTriples"))

    for filename in filenames:
        meta.write("%-30s %-11s %-9s %-9d %-8.2f %-10s\n" %
                   (filename, stats["Owlready2?"][filename], stats["Rdflib?"][filename], stats["NbErrors"][filename],
                    stats["Time"][filename], stats["NbTriples"][filename]))
    meta.write("\n")
    meta.write("%-30s %-11s %-9s %-9d %-8.2f %-10s\n" %
               ("Total", sum(stats["Owlready2?"].values()), sum(stats["Rdflib?"].values()),
                sum(stats["NbErrors"].values()), sum(stats["Time"].values()), sum(stats["NbTriples"].values())))
    meta.write("\n")
    meta.write("Nb of files: %d\n" % len(filenames))

    out.close()
    meta.close()
    print("\n§ Files \"%s\" and \"%s\" saved. " % (filepath_results, filepath_meta))


def classify_names():
    filepath_opd = "results/object_properties_database.txt"
    filepath_words = "results/words.txt"

    prefixes = ["a", "as", "at", "by", "for", "has", "in", "is", "of", "so", "the", "to"]
    suffixes = ["a", "as", "at", "by", "for", "has", "in", "is", "of", "so", "the", "to"]
    opd = open(filepath_opd, "r", encoding='utf-8', errors='ignore')
    _ = opd.readline().split(" ")
    opd.readline()
    results_pre = {}
    results_suf = {}

    nb_words = 0
    for line in opd:
        values = rem_empty(line.split(" "))
        values.pop()  # Remove '\n' at the end of the list
        op_name = values[0]
        words = split_name(op_name)

        prefixes_found = [prefix for prefix in prefixes if words[0].lower() == prefix]
        suffixes_found = [suffix for suffix in prefixes if words[-1].lower() == suffix]

        if prefixes_found != [] or suffixes_found != []:
            for prefix in prefixes_found:
                if prefix not in results_pre.keys():
                    results_pre[prefix] = []
                results_pre[prefix].append(op_name)

            for suffix in suffixes_found:
                if suffix not in results_suf.keys():
                    results_suf[suffix] = []
                results_suf[suffix].append(op_name)
        nb_words += 1
    opd.close()

    out = open(filepath_words, "w", encoding='utf-8', errors='ignore')
    for affix, words in results_pre.items():
        proportion = 100 * len(words) / nb_words
        out.write("Prefix \"%s\" (%d/%d, %.2f%%)\n" % (affix, len(words), nb_words, proportion))
        for word in words:
            out.write("%s, " % word)
        out.write("\n\n")

    for affix, words in results_suf.items():
        proportion = 100 * len(words) / nb_words
        out.write("Suffix \"%s\" (%d/%d, %.2f%%)\n" % (affix, len(words), nb_words, proportion))
        for word in words:
            out.write("%s, " % word)
        out.write("\n\n")

    out.close()
