
class WordDictionary:
    def __init__(self, filepath: str = None, caseSensitive: bool = True):
        if filepath is not None:
            self.loadFromFile(filepath, caseSensitive)
        else:
            self.__filepath = ""
            self.__data = set()
            self.__dataLower = set()

    def loadFromFile(self, filepath: str, caseSensitive: bool = True):
        """
            Load a TXT file chich contains the list of words. The file must contains only 1 word by line.
            :param filepath: The path to the file.
            :param caseSensitive: True if you want to store the case of the data.
        """
        fWords = open(filepath, "r", encoding="utf-8")
        self.__filepath = filepath
        self.__data = set()
        self.__dataLower = set()
        for line in fWords:
            word = line.replace("\n", "").lower()
            if caseSensitive:
                self.__data.add(word)
            self.__dataLower.add(word.lower())
        if not caseSensitive:
            self.__data = self.__dataLower
        fWords.close()

    def existsInDictionary(self, word: str, caseSensitive: bool = True) -> bool:
        """
            Check if the word exists.
            :param word: The word to check.
            :param caseSensitive: True if case must be considered.
            :return: Return True if the word is in WordDictionary.
        """
        if caseSensitive:
            return word in self.__data
        else:
            return word.lower() in self.__dataLower

    def filterUnknownWords(self, words: list, caseSensitive: bool = True) -> list:
        """
            Filter unknown words in "words" list.
            :param words: The str list to filter.
            :param caseSensitive: True if case must be considered.
            :return: The words which exists in dictionary.
        """
        return [word for word in words if self.existsInDictionary(word, caseSensitive)]

    def getUnknownWords(self, document) -> list:
        """
            Return the list of unknown words in document.
            :param document: List of words to analyze. Can be a str, a list of str or a list of list of str.
            :return: A list of str.
        """
        if isinstance(document, list):
            result = []
            for elt in document:
                result += self.getUnknownWords(elt)
            return result
        elif isinstance(document, str):
            return [] if self.existsInDictionary(document) else [document]
        else:
            raise Exception("Illegal argument: arg is not a list and not a str.")
