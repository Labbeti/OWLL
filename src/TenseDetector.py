from src.Csts import Csts


class TenseDetector:
    def __init__(self, filepath: str = None):
        if filepath is not None:
            self.load(filepath)
        else:
            self.__filepath = ""
            self.__verbs = []

    def load(self, filepath: str):
        self.__filepath = filepath
        self.__verbs = []
        file = open(filepath, "r", encoding="utf-8")
        for line in file:
            self.__verbs.append(line.split(","))
        file.close()

    def recognize(self, verb: str) -> (str, list):
        # Return the infinitive and tense of the verb
        tensesFound = []
        for verbTenses in self.__verbs:
            for i in range(len(verbTenses)):
                if verb == verbTenses[i]:
                    tensesFound.append(Csts.TENSES[i])
            if len(tensesFound) > 0:
                return verbTenses[0], tensesFound
        return None, None

    def clear(self):
        self.__filepath = ""
        self.__verbs = []
