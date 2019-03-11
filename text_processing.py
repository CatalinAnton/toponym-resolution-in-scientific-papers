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


def get_sentences(text):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)


def get_tokens(text):
    return nltk.tokenize.word_tokenize(text)


def get_pn_sentences(text):
    sentences = get_sentences(text)
    pn_sentences = list()

    for sentence in sentences:
        pos_sentence = preprocess(sentence)
        if is_NNP_sentence(pos_sentence):
            pn_sentences.append(sentence)

    return pn_sentences


def is_NNP_sentence(sentence):
    for t in sentence:
        if 'NNP' in t[1] or 'NNPS' in t[1]:
            return True
    return False
