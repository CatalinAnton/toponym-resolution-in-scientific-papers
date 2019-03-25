from nltk.corpus import wordnet as wn

def get_most_frequent_sense_for_word(word):
    for synset in wn.synsets(word):
        return synset.definition()

def get_sensens_of_word(word):
    list_senses = []
    for ss in wn.synsets(word):
        list_senses.append(ss.definition())
    return list_senses