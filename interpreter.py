from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class Interpreter:
    def __init__(self, lang):
        self.lang = lang

    def tokenize_filter_process(self, text):
        words = word_tokenize(text)
        stop_words = set(stopwords.words(self.lang))
        return [word for word in words if word.casefold() not in stop_words]
