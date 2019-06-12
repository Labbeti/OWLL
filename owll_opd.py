from OPD import OPD
from util import *

import sys


def gen_opd(args: list = None) -> int:
    """
        Generate the OPD file.
        :param args: Arguments from OWLL terminal:
            args[0] is the dirpath for searching ontologies.
            args[1] is the filepath for the OPD result file.
        :return: Exit code for OWLL terminal.
    """

    if args is not None and len(args) > 2:
        prt("Error: Unexpected number of arguments: %d" % len(args))
        return 1
    dirpathOnto, filepathOpd = get_args(args, [Csts.Paths.ONTOLOGIES, Csts.Paths.OPD])

    opd = OPD()
    opd.generate(dirpathOnto)
    opd.saveInFile(filepathOpd, True)
    return 0


if __name__ == "__main__":
    commandArgs = sys.argv[1:]
    gen_opd(commandArgs)
