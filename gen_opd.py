import sys
from src.CST import CST
from src.ontology.OPD import OPD
from src.util import get_args, prt, print_command_help


def print_help():
    """
        Print "gen_opd" command usage.
    """
    arg1 = "dirpath_to_owl_ontologies"
    arg2 = "filepath_result"
    print_command_help(
        "gen_opd [%s [%s]]" % (arg1, arg2),
        "Generate the OPD file with a directory that contains ontology files. This operation can take a long time if "
        "you have a large list of files.",
        [(arg1, CST.PATH.ONTOLOGIES), (arg2, CST.PATH.OPD)]
    )


def gen_opd(args: list = None) -> int:
    """
        Generate the OPD file.
        :param args: Arguments from terminal:
            args[0] is the dirpath for searching ontologies.
            args[1] is the filepath for the OPD result file.
        :return: Exit code for terminal.
    """

    if args is None or len(args) > 2 or "-h" in args or "-help" in args or "--help" in args:
        print_help()
        return 0

    dirpathOnto, filepathOpd = get_args(args, [CST.PATH.ONTOLOGIES, CST.PATH.OPD])
    opd = OPD()
    opd.generate(dirpathOnto)
    opd.saveInFile(filepathOpd, True)
    return 0


if __name__ == "__main__":
    commandArgs = sys.argv[1:]
    gen_opd(commandArgs)