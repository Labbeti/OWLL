from src.CST import CST


class TenseDetector:
    """
        Class for detect tense of a verb.
        Note: Currrently unused in OWLL.
    """

    def __init__(self, filepath: str = None):
        """
            Constructor of TenseDetector. Create a
            :param filepath:
        """
        if filepath is not None:
            self.load(filepath)
        else:
            self.__filepath = ""
            self.__verbs = []

    def load(self, filepath: str):
        """
            Load from a TXT file the list of verbs with theirs tenses.
            :param filepath: Path to the txt file.
        """
        self.__filepath = filepath
        self.__verbs = []
        file = open(filepath, "r", encoding="utf-8")
        for line in file:
            self.__verbs.append(line.split(","))
        file.close()

    def recognize(self, verb: str) -> (str, list):
        """
            Return the infinitive and tense of the verb
            :param verb:
            :return:
        """
        tensesFound = []
        for verbTenses in self.__verbs:
            for i in range(len(verbTenses)):
                if verb == verbTenses[i]:
                    tensesFound.append(CST.TENSES[i])
            if len(tensesFound) > 0:
                return verbTenses[0], tensesFound
        return None, None

    def clear(self):
        """
            Clear the data loaded.
        """
        self.__filepath = ""
        self.__verbs = []
