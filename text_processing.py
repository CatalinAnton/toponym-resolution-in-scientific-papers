import nltk
from langdetect import detect

def preprocess(text):
    text_tokenzied = nltk.word_tokenize(text)
    text_pos_tagged = nltk.pos_tag(text_tokenzied)
    return text_pos_tagged

def get_lemmas(text):
    text_tokenzied = nltk.word_tokenize(text)
    porter = nltk.PorterStemmer()
    list_lemma = []
    for token in text_tokenzied:
        list_lemma.append(porter.stem(token))
    return list_lemma

def get_language_of_text(text):
    return detect(text)