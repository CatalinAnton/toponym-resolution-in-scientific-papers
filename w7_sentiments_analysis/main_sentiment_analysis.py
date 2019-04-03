from textblob import TextBlob

import p1_file_management
import p3_sentence_splitter


def sentiment_alg(text_list):
    c_pos = 0
    c_neg = 0
    c_neut = 0
    for text in text_list:
        # print(text.text)
        analysis = TextBlob(text)
        print(analysis.sentiment)
        if analysis.sentiment[0] > 0:
            print("Positive")
            c_pos += 1
        elif analysis.sentiment[0] < 0:
            print("Negative")
            c_neg += 1
        else:
            print("Neutral")
            c_neut += 1
    print("positives:", c_pos)
    print("negatives:", c_neg)
    print("neutrals:", c_neut)
    return c_pos, c_neg, c_neut


sentiment_alg(["I love hamburgers", "Paris is in France"])

files = p1_file_management.get_file_list(p1_file_management.resource_location)
dict_file_content = p1_file_management.get_dictionary_file_content(files)

test_input = open('../resources/txt/1731092.txt')
test_input = test_input.read()
sentences = p3_sentence_splitter.get_sentences(test_input)

sentiment_alg(sentences)
