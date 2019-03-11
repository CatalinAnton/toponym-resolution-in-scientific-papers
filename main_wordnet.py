from nltk.corpus import wordnet as wn

# import nltk
# nltk.download('wordnet')

word = 'country'


def get_name(synset):
    return str(synset.name().split(".")[0].replace('_', ' '))


def get_list_of_synonyms(word):
    list_synonyms = []
    word_sysnonyms = wn.synsets(word)
    for word_synonym in word_sysnonyms:
        list_synonyms.append(get_name(word_synonym))
    return list_synonyms


def get_list_of_hypernyms(word):
    list_hypernyms = []
    word_sysnonyms = wn.synsets(word)
    word_hypernyms = word_sysnonyms[0].hypernyms()
    for word_hypernym in word_hypernyms:
        list_hypernyms.append(get_name(word_hypernym))
    return list_hypernyms


def get_list_of_hyponyms(word):
    list_hyponyms = []
    word_sysnonyms = wn.synsets(word)
    word_hypernyms = word_sysnonyms[0].hyponyms()
    for word_hyponym in word_hypernyms:
        list_hyponyms.append(get_name(word_hyponym))
    return list_hyponyms


def get_list_of_synonyms_stringify(word):
    string = 'Synonyms for ' + word + '\n' + str(get_list_of_synonyms(word))
    return string


def get_list_of_hypernyms_stringify(word):
    string = 'Hypernyms for ' + word + '\n' + str(get_list_of_hypernyms(word))
    return string


def get_list_of_hyponyms_stringify(word):
    string = 'Hyponyms for ' + word + '\n' + str(get_list_of_hyponyms(word))
    return string


print(get_list_of_synonyms_stringify(word))
print(get_list_of_hypernyms_stringify(word))
print(get_list_of_hyponyms_stringify(word))
