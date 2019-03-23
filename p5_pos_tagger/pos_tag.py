import nltk


def pos_tag(text_tokenzied):
    text_pos_tagged = nltk.pos_tag(text_tokenzied)
    return text_pos_tagged
