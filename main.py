from owll_clust import clust_op_names
from owll_stats import gen_opd
from owll_stats import connect_words_stats
from owll_stats import extract_words
from owll_typoclass import class_with_typo_words
from utils import prt


def menu():
    switch = {
        "1": class_with_typo_words,
        "2": clust_op_names,
        "3": gen_opd,
        "4": connect_words_stats,
        "5": extract_words,
    }
    leaving = False

    while not leaving:
        prt("-- MAIN MENU -- ")
        prt("1 - Try classify with typo words")
        prt("2 - Try clusterize with on names of object properties")
        prt("3 - Regenerate Object Property Database")
        prt("4 - Update connect words statistics")
        prt("5 - Try to extract root words")
        prt("0 - Quit")

        user_input = input("> ")
        if user_input == "0":
            leaving = True
        elif user_input in switch.keys():
            fct = switch[user_input]
            fct()
        else:
            print("Unknown command \"%s\"" % user_input)


def main():
    menu()


if __name__ == "__main__":
    main()
