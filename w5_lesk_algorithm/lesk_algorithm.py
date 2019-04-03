from nltk.wsd import lesk
from utils.get_set_of_words_from_sentence import *


# function returns None if a sense has not been found
# e.g. for the owrd 'Clin' or 'J' no sense will be found
def lesk_algorithm(word, sentence):
    word_list = get_set_of_words_from_sentence(sentence)
    synset_best_sense = lesk(word_list, word, 'n')
    if synset_best_sense:
        best_sense = synset_best_sense.definition()
        return best_sense
