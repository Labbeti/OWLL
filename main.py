import sys
from src.app import main
from src.autotests import test_all
from src.util import print_command_help


def print_help():
    print_command_help(
        "main.py",
        "Launch the OWLL Graphical User Interface to customize object property clusterisation."
    )


if __name__ == "__main__":
    args = sys.argv[1:]

    if "-h" in args or "-help" in args or "--help" in args:
        print_help()
    elif "-autotests" in args:
        test_all()
    else:
        main()
