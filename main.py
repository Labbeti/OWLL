import sys
from src.app import main
from src.autotests import test_all
from src.CST import CST
from src.util import print_command_help, init_cst_from_args


def print_help():
    """
        Print in terminal the help for "main.py".
    """
    arg1 = "-verbose"
    arg2 = "-debug"
    arg3 = "-load_default_files"
    print_command_help(
        "main.py [%s] [%s] [%s]" % (arg1, arg2, arg3),
        "Launch the OWLL Graphical User Interface to customize object property clusterisation. \n"
        "At initialisation, this command can load files \"%s\" and \"%s\" with option \"%s\"." % (
            CST.PATH.OPD, CST.PATH.CLUSTER_MODEL, arg3
        ),
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    init_cst_from_args(args)
    CST.LOAD_DEFAULTS_FILES = "-load_default_files" in args

    if "-h" in args or "-help" in args or "--help" in args:
        print_help()
    elif "-autotests" in args:
        test_all()
    else:
        main()
