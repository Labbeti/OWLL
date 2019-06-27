import sys
from src.CST import CST
from src.file_io import create_result_file
from src.models.ontology.OPD import OPD
from src.util import print_command_help, str_list_lower, to_percent, get_args, prt, init_cst_from_args
from src.WordDictionary import WordDictionary


def searched_words_stats(opd: OPD, filepathResults: str):
    """
        Generate some stats about connect word (Config.Words.getWordsSearched()) in "connect_words_stats.txt"
        :param opd: OPD to use.
        :param filepathResults: path to result file.
    """
    results = {word_type: {} for word_type in ["Prefix", "Suffix", "Infix"]}

    for opData in opd.getData():
        opNameSplit = str_list_lower(opData.getNameSplit())

        fctWordsFound = [fctWord for fctWord in CST.WORDS.getWordsSearched() if fctWord in opNameSplit]
        fctWordsPosition = [(
            "Prefix" if word == opNameSplit[0] else
            "Suffix" if word == opNameSplit[-1] else
            "Infix") for word in fctWordsFound]

        for i in range(len(fctWordsFound)):
            wordsFound = fctWordsFound[i]
            wordsPos = fctWordsPosition[i]
            if wordsFound not in results[wordsPos].keys():
                results[wordsPos][wordsFound] = []
            results[wordsPos][wordsFound].append(opData.getName())

    out = create_result_file(filepathResults, opd.getSrcpath(), opd.getVersion())
    out.write("# Words searched are : %s\n" % str(CST.WORDS.getWordsSearched()))
    out.write("\n")

    sortedResults = []
    for word_type, _ in results.items():
        for wordsFound, words in results[word_type].items():
            proportion = 100 * len(words) / opd.getSize()
            sortedResults.append((proportion, word_type, wordsFound, words))

    sortedResults.sort(key=lambda x: x[0], reverse=True)

    for (proportion, word_type, wordsFound, words) in sortedResults:
        out.write("%s: Word \"%s\" %d/%d (%.2f%%)\n" % (
            word_type, wordsFound, len(words), opd.getSize(), proportion))
        for word in words:
            out.write("%s, " % word)
        out.write("\n\n")

    out.close()


def extract_content_word(opd: OPD, filepathCW: str, filepathLists: str):
    """
        Generate a partition of op names in "content_words.txt" and "op_lists.txt"
        :param opd: OPD to use.
        :param filepathCW: the path of the list of content words found in OPD.
        :param filepathLists: the path of the lists of differents OP order by their number of content words.
    """
    names = {}
    contentWords = []
    allNamesSet = set()

    for opData in opd.getData():
        opName = opData.getName()
        # Rem Connect Words, Domain and Range
        wordsFiltered = opData.getNameSplit(True, True, CST.WORDS.getWordsSearched())

        nbWords = len(wordsFiltered)
        if nbWords not in names.keys():
            names[nbWords] = []
        names[nbWords].append(opName)
        allNamesSet.add(opName)
        if nbWords == 1:
            contentWords.append("".join(wordsFiltered))

    out = create_result_file(filepathLists, opd.getSrcpath(), opd.getVersion())
    out.write("# Words searched are : %s\n" % str(CST.WORDS.getWordsSearched()))
    out.write("# The followings lists contains OP names when deleting domain, range and words searched:\n\n")

    names_sort = list(names.items())
    names_sort.sort(key=lambda x: x[0], reverse=False)

    for nbWords, namesWithNbWords in names_sort:
        namesWithNbWordsSet = set(namesWithNbWords)
        proportionElements = to_percent(len(namesWithNbWords), len(opd.getData()))
        proportionUniques = to_percent(len(namesWithNbWordsSet), len(allNamesSet))
        out.write("Names with %d words remaining: [ elements = %d/%d (%.2f%%) | uniques = %d/%d (%.2f%%) ]\n" % (
            nbWords, len(namesWithNbWords), len(opd.getData()), proportionElements, len(namesWithNbWordsSet),
            len(allNamesSet), proportionUniques
        ))

        i = 0
        for name in namesWithNbWords:
            out.write("%s, " % name)
            i += 1
            if i % 100 == 0:
                out.write("\n")
        out.write("\n\n")
    out.close()

    out = create_result_file(filepathCW, opd.getSrcpath(), opd.getVersion())
    out.write("# These lists can contains duplicates.\n")
    out.write("# Content words of OP with 1 content word (%d): \n" % len(contentWords))
    for name in contentWords:
        out.write("%s\n" % name)
    out.close()


def generate_global_stats(opd: OPD, filepathResults: str):
    """
        Generate some stats in "stats.txt"
        :param opd: OPD to use.
        :param filepathResults: the path where to put results.
    """

    columnsNames = ("ObjectPropertySplit", "Has1CW?", "ContentWord", "Domain", "Range")
    columnsFormat = "| %-35s | %-8s | %-30s | %-6s | %-6s | "
    lineFormat = "| %-35s | %-8d | %-30s | %-6d | %-6d | "
    allContentWords = []
    opNames = []

    out = create_result_file(filepathResults, opd.getSrcpath(), opd.getVersion())
    out.write("# Words searched are : %s\n" % str(CST.WORDS.getWordsSearched()))
    out.write("# Note: CW = Content Word\n\n")

    out.write(columnsFormat % columnsNames)
    for conn in CST.WORDS.getWordsSearched():
        out.write("%-5s | " % conn)
    out.write("\n\n")

    # Generate the big matrix of booleans for statistics.
    counter = {
        key: [None for _ in range(opd.getSize())]
        for key in (["Domain", "Range"] + CST.WORDS.getWordsSearched())
    }
    i = 0
    for opData in opd.getData():
        opName = opData.getName()
        opNameSplit = opData.getNameSplit()
        nbWords = len(opNameSplit)

        # The difference between new and old splitted is the number of values erased
        counter["Domain"][i] = nbWords - len(opData.getNameSplit(filterDomain=True))
        # Erase range
        counter["Range"][i] = nbWords - len(opData.getNameSplit(filterRange=True))
        # Erase function words one by one to get the number of words deleted for each erasure
        for word in CST.WORDS.getWordsSearched():
            counter[word][i] = nbWords - len(opData.getNameSplit(filterSubWords=[word]))

        # Get CW
        contentWords = opData.getNameSplit(
            filterDomain=True, filterRange=True, filterSubWords=CST.WORDS.getWordsSearched())
        has1CW = len(contentWords) == 1
        contentWordsStr = ("".join(contentWords)) if has1CW else ""

        # Write line in result file
        out.write(lineFormat % (
            " ".join(opNameSplit), has1CW, contentWordsStr, counter["Domain"][i], counter["Range"][i]))
        for conn in CST.WORDS.getWordsSearched():
            out.write("%-5d | " % counter[conn][i])
        out.write("\n")

        # Update lists
        if has1CW:
            allContentWords.append(contentWordsStr.lower())
        opNames.append(opName.lower())
        i += 1

    # Write columns names in the end
    out.write("\n\n")
    out.write(columnsFormat % columnsNames)
    for conn in CST.WORDS.getWordsSearched():
        out.write("%-5s | " % conn)

    # Write sums for each columns
    out.write("\nTotal:\n")
    out.write(lineFormat % (opd.getSize(), len(allContentWords), "", sum(counter["Domain"]), sum(counter["Range"])))
    for conn in CST.WORDS.getWordsSearched():
        out.write("%-5d | " % sum(counter[conn]))

    # Write proportions for each columns in %
    out.write("\nProportions (%):\n")
    out.write("| %-35.2f | %-8.2f | %-30s | %-6.2f | %-6.2f | " % (
        100, to_percent(len(allContentWords), opd.getSize()), "", to_percent(sum(counter["Domain"]), opd.getSize()),
        to_percent(sum(counter["Range"]), opd.getSize())))

    for conn in CST.WORDS.getWordsSearched():
        out.write("%-5.2f | " % to_percent(sum(counter[conn]), opd.getSize()))
    out.write("\n\n")

    # Write additional information and close result file
    out.write("Distinct content words = %d\n" % len(set(allContentWords)))
    out.write("Distinct OP = %d\n" % len(set(opNames)))
    out.close()


def gen_unknown_words(opd: OPD, filepathWords: str, filepathUnusedWords: str):
    """
        Generate a list of words of OP names not found in the language list found in filepathWords.
        :param filepathWords: list of words of a language.
        :param opd: OPD to use.
        :param filepathUnusedWords: path to result file.
    """

    wDict = WordDictionary(filepathWords)

    unusedWordsData = []
    for opData in opd.getData():
        filepath = opData.src
        opName = opData.getName()
        opNameSplit = str_list_lower(opData.getNameSplit())
        for subWord in opNameSplit:
            if wDict.existsInDictionary(subWord):
                unusedWordsData.append((subWord, opName, filepath))

    # Generate a result file with unrecognized words.
    fUnusedWords = create_result_file(filepathUnusedWords)
    fUnusedWords.write("# This file contains non-english words found when creating OPD.\n\n")
    fUnusedWords.write("%-30s %-45s %-40s\n\n" % ("Word", "ObjectProperty", "Filename"))
    for subWord, opName, file in unusedWordsData:
        fUnusedWords.write("%-30s %-45s %-40s\n" % (subWord, opName, file))
    fUnusedWords.close()


def gen_particle_pairs_stats(opd: OPD, filepathResults: str):
    fctWords = CST.WORDS.getWordsSearched()
    aloneColumn = "[alone]"
    totalColumn = "[nbOcc]"
    lines = fctWords
    columns = fctWords + [aloneColumn, totalColumn]
    stats = {
        key1: {
            key2: 0 for key2 in columns
        }
        for key1 in lines
    }
    for opData in opd.getData():
        opNameSplit = str_list_lower(opData.getNameSplit())

        for word in fctWords:
            if word in opNameSplit:
                opNameSplitWithoutWord = [w for w in opNameSplit if w != word]
                isAlone = True
                for word2 in fctWords:
                    if word2 in opNameSplitWithoutWord:
                        stats[word][word2] += 1
                        isAlone = False
                if isAlone:
                    stats[word][aloneColumn] += 1
                stats[word][totalColumn] += 1

    fRes = create_result_file(filepathResults, opd.getSrcpath(), opd.getVersion())

    fRes.write("# Matrix in %: \n")
    fRes.write("%-7s " % "")
    for name in columns:
        fRes.write("%-7s " % name)
    fRes.write("\n")
    for word, subDict in stats.items():
        fRes.write("%-7s " % word)
        for _, nb in subDict.items():
            fRes.write("%-7.1f " % to_percent(nb, subDict[totalColumn]))
        fRes.write("\n")
    fRes.write("\n")

    fRes.write("# Matrix in values: \n")
    fRes.write("%-7s " % "")
    for name in columns:
        fRes.write("%-7s " % name)
    fRes.write("\n")
    for word, subDict in stats.items():
        fRes.write("%-7s " % word)
        for _, nb in subDict.items():
            fRes.write("%-7d " % nb)
        fRes.write("\n")
    fRes.write("\n")
    fRes.close()


def print_help():
    """
        Print "gen_stats" command usage.
    """
    arg1 = "filepath_opd"
    print_command_help(
        "gen_opd [%s]" % arg1,
        "Generate statistics in files about function words and content words from an OPD.",
        [(arg1, CST.PATH.OPD)]
    )


def gen_stats(args_: list = None) -> int:
    """
        Update all statistics with an OPD.
        :param args_: Arguments from terminal.
        :return: Exit code for terminal.
    """

    if args_ is None or len(args_) > 2 or "-h" in args_ or "-help" in args_ or "--help" in args_:
        print_help()
        return 0

    opdFilepath = get_args(args_, [CST.PATH.OPD])[0]

    prt("Compute statistics with OPD \"%s\"..." % opdFilepath)
    opd = OPD()
    opd.loadFromFile(opdFilepath)

    prt("Step %d/%d: Update searched words statistics in \"%s\"..." % (1, 5, CST.PATH.STATS_SEARCHED_WORDS))
    searched_words_stats(opd, CST.PATH.STATS_SEARCHED_WORDS)

    prt("Step %d/%d: Extract content words in \"%s\"..." % (2, 5, CST.PATH.STATS_LISTS))
    extract_content_word(opd, CST.PATH.STATS_CW, CST.PATH.STATS_LISTS)

    prt("Step %d/%d: Generate content words global statistics in \"%s\"..." % (3, 5, CST.PATH.STATS_GLOBAL))
    generate_global_stats(opd, CST.PATH.STATS_GLOBAL)

    prt("Step %d/%d: Extract non-english words from opd in \"%s\"..." % (4, 5, CST.PATH.NON_EN_WORDS))
    gen_unknown_words(opd, CST.PATH.ENGLISH_WORDS, CST.PATH.NON_EN_WORDS)

    prt("Step %d/%d: Update searched words probability matrix in \"%s\"..." % (5, 5, CST.PATH.STATS_PAIRS_SW))
    gen_particle_pairs_stats(opd, CST.PATH.STATS_PAIRS_SW)

    prt("Statistics done in directory \"%s\"." % "results/stats/")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    init_cst_from_args(args)
    gen_stats(args)
