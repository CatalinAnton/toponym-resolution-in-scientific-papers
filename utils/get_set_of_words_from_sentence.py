from nltk.tokenize import RegexpTokenizer

def get_set_of_words_from_sentence(sentence):
    tokenizer = RegexpTokenizer(r'\w+') # get just words
    return tokenizer.tokenize(sentence)