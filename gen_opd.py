import sys
from src.CST import CST
from src.models.ontology.OPD import OPD
from src.util import get_args, print_command_help, init_cst_from_args


def print_help():
    """
        Print "gen_opd" command usage.
    """
    arg1 = "dirpath_to_owl_ontologies"
    arg2 = "filepath_result"
    arg3 = "-verbose"
    print_command_help(
        "gen_opd [%s [%s]] [%s]" % (arg1, arg2, arg3),
        "Generate the OPD file with a directory that contains ontology files. This operation can take a long time if "
        "you have a large list of files.",
        [(arg1, CST.PATH.ONTOLOGIES), (arg2, CST.PATH.OPD)]
    )


def gen_opd(args_: list = None) -> int:
    """
        Generate the OPD file.
        :param args_: Arguments from terminal:
            args[0] is the dirpath for searching ontologies.
            args[1] is the filepath for the OPD result file.
        :return: Exit code for terminal.
    """

    if args_ is None or len(args_) > 2 or "-h" in args_ or "-help" in args_ or "--help" in args_:
        print_help()
        return 0

    dirpathOnto, filepathOpd = get_args(args_, [CST.PATH.ONTOLOGIES, CST.PATH.OPD])
    opd = OPD()
    opd.generateFromDir(dirpathOnto)
    opd.saveInFile(filepathOpd, True)
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    init_cst_from_args(args)
    gen_opd(args)
