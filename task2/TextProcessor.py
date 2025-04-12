import itertools
from pymorphy3 import MorphAnalyzer
import re
import spacy
import nltk
from nltk.corpus import stopwords


class TextProcessor:
    PATTERN_WORDS = r"[а-яА-ЯёЁ]+(?:-[а-яА-ЯёЁ]+)*"  # Слова с дефисами
    PATTERN_NUMBERS = r"\d+[.,]?\d*"  # Числа (task1, task2.5)  \d+([.,]\d+)*
    PATTERN_PUNCTUATION = r"[.,!?;:]+"  # Пунктуация
    PATTERN_QUOTES_BRACKETS = r"[«»\"“”(){}—]"  # Скобки/кавычки
    PATTERN_FALLBACK = r"\S"  # Фолбэк (остальное)

    def __init__(self):
        nltk.download('stopwords')
        self.morph = MorphAnalyzer()
        self.nlp = spacy.load("ru_core_news_sm")
        self.russian_stopwords = stopwords.words('russian')

    def is_stop_word(self, word):
        return word in self.russian_stopwords

    def lemmatize_morph(self, word):
        return self.morph.parse(word)[0].normal_form

    def word_tokenize(self, text):
        patterns = [TextProcessor.PATTERN_WORDS]
        tokens = [re.findall(pattern, text) for pattern in patterns]
        return list(itertools.chain(*tokens))
