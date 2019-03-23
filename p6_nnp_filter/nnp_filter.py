def is_NNP_sentence(pos_tagged_sentence):
    for tag in pos_tagged_sentence:
        if 'NNP' in tag[1] or 'NNPS' in tag[1]:
            return True
    return False