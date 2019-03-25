# <lemma>.<pos>.<number>

def get_synset_lemma_by_index(synset, index):
    i = 1
    for lemma in synset.lemmas():
        if i == index:
            return lemma.name
        i += 1

def get_synset_pos_tag(synset):
    return synset.pos()

def get_synset_sense_number(synset):
    print(synset.lexname())