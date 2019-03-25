from w6_lesk_algorithm.lesk_algorithm import *
from utils.senses import *


# simple lesk example
def lesk_example(word, sentence):
    best_sense_paris = lesk_algorithm(word, sentence)
    print('Best sense for ', word, ' -> ', best_sense_paris)
    print('Senses for', word)
    senses = get_sensens_of_word(word)
    for sense in senses:
        print('\t', sense)


sentence = 'I read about the life of Prince Paris last week.'
word = 'Paris'
lesk_example(word, sentence)
print()

sentence = 'I have pine cones... here, in my garden'
word = 'pine'
lesk_example(word, sentence)
print()
