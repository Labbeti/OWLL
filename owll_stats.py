from file_io import create_result_file
from owll_opd import read_opd
from util import *


def __filter_op_name_split(opNameSplit: list, opDomain: str, opRange: str) -> list:
    return [word for word in opNameSplit
            if word.lower() != opDomain.lower()
            and word.lower() != opRange.lower()
            and word.lower() not in Consts.Word.getWordsSearched()]


# Generate some stats about connect word (Config.Words.getWordsSearched()) in "connect_words_stats.txt"
def searched_words_stats(filepathOPD: str, filepathResults: str):
    results = {word_type: {} for word_type in ["Prefix", "Suffix", "Infix"]}

    data, versionOPD, _ = read_opd(filepathOPD)
    for values in data:
        op_name = values["ObjectProperty"]
        words_name = split_op_name(op_name)
        words_name = [word.lower() for word in words_name]

        conn_words_found = [conn_word for conn_word in Consts.Word.getWordsSearched() if conn_word in words_name]
        conn_words_type = [("Prefix" if word == words_name[0] else
                            "Suffix" if word == words_name[-1] else
                            "Infix") for word in conn_words_found]

        for i in range(len(conn_words_found)):
            conn_word_found = conn_words_found[i]
            conn_word_type = conn_words_type[i]
            if conn_word_found not in results[conn_word_type].keys():
                results[conn_word_type][conn_word_found] = []
            results[conn_word_type][conn_word_found].append(op_name)

    out = create_result_file(filepathResults, filepathOPD, versionOPD)
    out.write("# Words searched are : %s\n" % str(Consts.Word.getWordsSearched()))
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
def extract_roots(filepathOPD: str, filepathRoots: str, filepathLists: str):
    names = {}
    rootsOnly = []
    allNamesSet = set()
    data, versionOPD, _ = read_opd(filepathOPD)

    for values in data:
        opName = values["ObjectProperty"]
        opDomain = values["Domain"]
        opRange = values["Range"]
        opNameSplit = split_op_name(opName)

        # Rem Connect Words, Domain and Range
        wordsFiltered = __filter_op_name_split(opNameSplit, opDomain, opRange)

        nbWords = len(wordsFiltered)
        if nbWords not in names.keys():
            names[nbWords] = []
        names[nbWords].append(opName)
        allNamesSet.add(opName)
        if nbWords == 1:
            rootsOnly.append("".join(wordsFiltered))

    out = create_result_file(filepathLists, filepathOPD, versionOPD)
    out.write("# Words searched are : %s\n" % str(Consts.Word.getWordsSearched()))
    out.write("# The followings lists contains OP names when deleting domain, range and words searched:\n\n")

    for nbWords, namesWithNbWords in names.items():
        namesWithNbWordsSet = set(namesWithNbWords)
        proportionElements = to_percent(len(namesWithNbWords), len(data))
        proportionUniques = to_percent(len(namesWithNbWordsSet), len(allNamesSet))
        out.write("Names with %d words remaining: [ elements = %d/%d (%.2f%%) | uniques = %d/%d (%.2f%%) ]\n" % (
            nbWords, len(namesWithNbWords), len(data), proportionElements, len(namesWithNbWordsSet), len(allNamesSet), proportionUniques
        ))

        i = 0
        for name in namesWithNbWords:
            out.write("%s, " % name)
            i += 1
            if i % 100 == 0:
                out.write("\n")
        out.write("\n\n")
    out.close()

    out = create_result_file(filepathRoots, filepathOPD, versionOPD)
    out.write("# These lists can contains duplicates.\n")
    out.write("# Root words (%d): \n" % len(rootsOnly))
    for name in rootsOnly:
        out.write("%s\n" % name)
    out.close()


# Generate some stats in "stats.txt"
def generate_global_stats(filepathOPD: str, filepathResults: str):
    data, versionOpd, _ = read_opd(filepathOPD)
    columnsNames = ("ObjectProperty", "HasRoot?", "Root", "Domain", "Range")
    columnsFormat = "| %-35s | %-8s | %-30s | %-6s | %-6s | "
    lineFormat = "| %-35s | %-8d | %-30s | %-6d | %-6d | "
    roots = []
    opNames = []

    out = create_result_file(filepathResults, filepathOPD, versionOpd)
    out.write("# Words searched are : %s\n" % str(Consts.Word.getWordsSearched()))
    out.write("\n")

    out.write(columnsFormat % columnsNames)
    for conn in Consts.Word.getWordsSearched():
        out.write("%-5s | " % conn)
    out.write("\n\n")

    i = 0
    counter = {key: [None for _ in range(len(data))] for key in (["Domain", "Range"] + Consts.Word.getWordsSearched())}
    for values in data:
        opName = values["ObjectProperty"]
        opDomain = values["Domain"]
        opRange = values["Range"]

        # TODO : clean here
        splitted = split_op_name(opName)
        # Erase domain
        splittedWithoutD = [word for word in splitted if word.lower() != opDomain.lower()]
        # The difference between new and old splitted is the number of values erased
        counter["Domain"][i] = len(splitted) - len(splittedWithoutD)
        # Erase range
        splittedWithoutDR = [word for word in splittedWithoutD if word.lower() != opRange.lower()]
        counter["Range"][i] = len(splittedWithoutD) - len(splittedWithoutDR)

        # Erase connect words one by one to get the number of words deleted for each erasure
        oldSplitted = splittedWithoutDR
        for conn in Consts.Word.getWordsSearched():
            newSplitted = [word for word in oldSplitted if word.lower() != conn.lower()]
            counter[conn][i] = len(oldSplitted) - len(newSplitted)
            oldSplitted = newSplitted

        # Get root
        rootWords = oldSplitted
        isRoot = len(rootWords) == 1
        root = ("".join(rootWords)) if isRoot else ""

        # Write line in result file
        out.write(lineFormat % (opName, isRoot, root, counter["Domain"][i], counter["Range"][i]))
        for conn in Consts.Word.getWordsSearched():
            out.write("%-5d | " % counter[conn][i])
        out.write("\n")

        # Update lists
        if isRoot:
            roots.append(root.lower())
        opNames.append(opName.lower())
        i += 1

    # Write columns names in the end
    nbProps = len(data)
    out.write("\n\n")
    out.write(columnsFormat % columnsNames)
    for conn in Consts.Word.getWordsSearched():
        out.write("%-5s | " % conn)

    # Write sums for each columns
    out.write("\nTotal:\n")
    out.write(lineFormat % (len(data), len(roots), "", sum(counter["Domain"]), sum(counter["Range"])))
    for conn in Consts.Word.getWordsSearched():
        out.write("%-5d | " % sum(counter[conn]))

    # Write proportions for each columns in %
    out.write("\nProportions (%):\n")
    out.write("| %-35.2f | %-8.2f | %-30s | %-6.2f | %-6.2f | " % (100, to_percent(len(roots), nbProps), "",
                                                                   to_percent(sum(counter["Domain"]), nbProps),
                                                                   to_percent(sum(counter["Range"]), nbProps)))
    for conn in Consts.Word.getWordsSearched():
        out.write("%-5.2f | " % to_percent(sum(counter[conn]), nbProps))
    out.write("\n\n")

    # Write additional information and close result file
    out.write("Distinct root words = %d\n" % len(set(roots)))
    out.write("Distinct OP = %d\n" % len(set(opNames)))
    out.close()


# Update all statistics with an OPD.
def update_all_stats(_: list = None) -> int:
    prt("Compute statistics with OPD...")
    searched_words_stats(Consts.Path.File.Result.OPD, Consts.Path.File.Result.STATS_SEARCHED_WORDS)
    extract_roots(Consts.Path.File.Result.OPD, Consts.Path.File.Result.STATS_ROOTS, Consts.Path.File.Result.STATS_LISTS)
    generate_global_stats(Consts.Path.File.Result.OPD, Consts.Path.File.Result.STATS_GLOBAL)
    prt("Statistics done in directory \"%s\"." % "results/stats/")
    return 0


if __name__ == "__main__":
    update_all_stats()
