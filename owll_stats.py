from owll_opd import read_opd
from util import *


# Generate some stats about connect word (Config.CONNECT_WORDS) in "connect_words_stats.txt"
def connect_words_stats():
    filepath_opd = "results/opd/opd.txt"
    filepath_words = "results/stats/connect_words_stats.txt"

    results = {word_type: {} for word_type in ["Prefix", "Suffix", "Inside"]}

    data, version_opd, _ = read_opd(filepath_opd)
    for values in data:
        op_name = values["ObjectProperty"]
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


# Generate a partition of op names in "roots.txt" and "roots_meta.txt"
def extract_roots():
    filepath_opd = "results/opd/opd.txt"
    filepath_meta = "results/stats/roots_meta.txt"
    filepath_results = "results/stats/roots.txt"

    root_names = []
    roots = []
    empty_names = []
    other_names = []
    data, version_opd, _ = read_opd(filepath_opd)

    for values in data:
        op_name = values["ObjectProperty"]
        words_name = split_name(op_name)

        # Rem Connect Words
        words_without_cw = [word for word in words_name if word.lower() not in Config.CONNECT_WORDS]
        op_domain = values["Domain"]
        op_range = values["Range"]
        # Rem Connect Words, Domain and Range
        words_without_cwdr = [word for word in words_without_cw
                              if word.lower() != op_domain.lower() and word.lower() != op_range.lower()]

        if len(words_without_cwdr) == 1:
            root_names.append(op_name)
            roots.append(words_without_cwdr[0].lower())
        elif len(words_without_cwdr) == 0:
            empty_names.append(op_name)
        else:
            other_names.append(op_name)

    out = open(filepath_meta, "w", encoding="utf-8")
    out.write("#! Version: %s\n" % get_time())
    out.write("# This file has been generated with the file \"%s\" (version %s)\n" % (filepath_opd, version_opd))
    out.write("# Words searched are : %s\n\n" % str(Config.CONNECT_WORDS))

    proportion = 100 * len(root_names) / len(data)
    out.write("Root words %d/%d (%.2f%%), (unique = %d)\n" % (len(root_names), len(data), proportion, len(set(roots))))
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
    out.write("# This list can contains duplicates.\n")
    out.write("# Root words: \n")
    for word in roots:
        out.write("%s\n" % word)
    out.close()


# Generate some stats in "stats.txt"
def generate_global_stats():
    filepathOpd = "results/opd/opd.txt"
    filepathResults = "results/stats/stats.txt"

    data, versionOpd, _ = read_opd(filepathOpd)
    columnsNames = ("ObjectProperty", "HasRoot?", "Root", "Domain", "Range")
    columnsFormat = "| %-35s | %-8s | %-30s | %-6s | %-6s | "
    lineFormat = "| %-35s | %-8d | %-30s | %-6d | %-6d | "
    roots = []
    opNames = []

    out = open(filepathResults, "w", encoding="utf-8")
    out.write("#! Version: %s\n" % get_time())
    out.write("# This file has been generated with the file \"%s\" (version %s)\n" % (filepathOpd, versionOpd))
    out.write("# Words searched are : %s\n" % str(Config.CONNECT_WORDS))
    out.write("\n")

    out.write(columnsFormat % columnsNames)
    for conn in Config.CONNECT_WORDS:
        out.write("%-5s | " % conn)
    out.write("\n\n")

    i = 0
    counter = {key: [None for _ in range(len(data))] for key in (["Domain", "Range"] + Config.CONNECT_WORDS)}
    for values in data:
        opName = values["ObjectProperty"]
        opDomain = values["Domain"]
        opRange = values["Range"]

        # TODO : clean here
        splitted = split_name(opName)
        splittedWithoutD = [word for word in splitted if word.lower() != opDomain.lower()]
        splittedWithoutDR = [word for word in splittedWithoutD if word.lower() != opRange.lower()]
        oldSplitted = splittedWithoutDR
        counter["Domain"][i] = len(splitted) - len(splittedWithoutD)
        counter["Range"][i] = len(splittedWithoutD) - len(splittedWithoutDR)
        for conn in Config.CONNECT_WORDS:
            newSplitted = [word for word in oldSplitted if word.lower() != conn.lower()]
            counter[conn][i] = len(oldSplitted) - len(newSplitted)
            oldSplitted = newSplitted

        rootWords = oldSplitted
        isRoot = len(rootWords) == 1
        root = ("".join(rootWords))
        out.write(lineFormat % (opName, isRoot, root, counter["Domain"][i], counter["Range"][i]))
        for conn in Config.CONNECT_WORDS:
            out.write("%-5d | " % counter[conn][i])
        out.write("\n")

        if isRoot:
            roots.append(root.lower())
        opNames.append(opName.lower())
        i += 1

    nbProps = len(data)
    out.write("\n\n")
    out.write(columnsFormat % columnsNames)
    for conn in Config.CONNECT_WORDS:
        out.write("%-5s | " % conn)

    out.write("\nTotal:\n")
    out.write(lineFormat % (len(data), len(roots), "", sum(counter["Domain"]), sum(counter["Range"])))
    for conn in Config.CONNECT_WORDS:
        out.write("%-5d | " % sum(counter[conn]))
    out.write("\nProportions (%):\n")
    out.write("| %-35.2f | %-8.2f | %-30s | %-6.2f | %-6.2f | " % (100, to_percent(len(roots), nbProps), "",
                                                                   to_percent(sum(counter["Domain"]), nbProps),
                                                                   to_percent(sum(counter["Range"]), nbProps)))
    for conn in Config.CONNECT_WORDS:
        out.write("%-5.2f | " % to_percent(sum(counter[conn]), nbProps))
    out.write("\n\n")

    out.write("Distinct root words = %d\n" % len(set(roots)))
    out.write("Distinct OP = %d\n" % len(set(opNames)))
    out.close()


def update_all_stats(args: str):
    prt("Compute statistics with OPD...")
    connect_words_stats()
    extract_roots()
    generate_global_stats()
    prt("Statistics done (in directory %s)." % "results/stats/")


if __name__ == "__main__":
    update_all_stats()
