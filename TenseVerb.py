class TenseVerb:
    TENSES = [
        "infinitive",
        "1st singular present",
        "2nd singular present",
        "3rd singular present",
        "present plural",
        "present participle",
        "1st singular past",
        "2nd singular past",
        "3rd singular past",
        "past plural",
        "past",
        "past participle",
    ]
    TENSES_INDEXES = {TENSES[i]: i for i in range(len(TENSES))}

    def __init__(self, filepath: str = None):
        if filepath is not None:
            self.load(filepath)
        else:
            self.__filepath = ""
            self.__verbs = []

    def load(self, filepath: str):
        self.__filepath = filepath
        self.__verbs = set()
        file = open(filepath, "r", encoding="utf-8")
        for line in file:
            self.__verbs.add(line.split(","))
        file.close()

    def recognize(self, verb: str) -> (str, str):
        # Return the infinitive and tense of the verb
        for verbTenses in self.__verbs:
            for i in range(len(verbTenses)):
                if verb == verbTenses[i]:
                    return verbTenses[0], TenseVerb.TENSES[i]
        return None, None

    def clear(self):
        self.__filepath = ""
        self.__verbs = []
