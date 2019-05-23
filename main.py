from onto_stats import *


# TODO : update
def menu():
    leaving = False
    while not leaving:
        prt("-- MAIN MENU -- ")
        prt("0 - Quit")

        user_input = input("> ")
        if user_input == "0":
            leaving = True


def main():
    menu()


if __name__ == "__main__":
    main()
