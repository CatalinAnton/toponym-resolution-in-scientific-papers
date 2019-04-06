from textblob import TextBlob

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