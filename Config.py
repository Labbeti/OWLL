
class Config:
    CONSOLE_PREFIX = "§ "
    RDFLIB_FORMATS = ['xml', 'n3', 'nt', 'trix', 'rdfa']
    VERBOSE_MODE = True
    LINK_WORDS = ["a", "as", "at", "by", "for", "has", "in", "is", "of", "so", "the", "to", "with"]


def prt(*arg):
    if Config.VERBOSE_MODE:
        print(Config.CONSOLE_PREFIX, end='')
        print(*arg)
