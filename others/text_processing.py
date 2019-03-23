import nltk
import p5_pos_tagger
from langdetect import detect


def get_lemmas(text):
    text_tokenzied = nltk.word_tokenize(text)
    porter = nltk.PorterStemmer()
    list_lemma = []
    for token in text_tokenzied:
        list_lemma.append(porter.stem(token))
    return list_lemma


def get_language_of_text(text):
    return detect(text)


def get_pn_sentences(text):
    sentences = get_sentences(text)
    pn_sentences = list()

    for sentence in sentences:
        pos_sentence = p5_pos_tagger.pos_tag(sentence)
        if is_NNP_sentence(pos_sentence):
            pn_sentences.append(sentence)

    return pn_sentences


def is_NNP_sentence(sentence):
    for t in sentence:
        if 'NNP' in t[1] or 'NNPS' in t[1]:
            return True
    return False
