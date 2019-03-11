import nltk
import re
from file_management import get_file_list
from file_management import get_dictionary_file_content
from text_processing import get_tokens

ann_file = open('1731092.ann')
txt_file = open('1731092.txt')

ann_data = ann_file.read()
txt_data = txt_file.read()


# T63	Location 9134 9143	Champaign
def extract_tf_words(ann_data):
    words =list()
    ann_words = re.findall(r'[T]{1}\d+\s+Location\s+\d+\s+\d+\s+\w+', ann_data)
    print(ann_words)

    for line in ann_words:
        print(line)
        words.append(line.split('\t')[2])

    print(words)
    return words


# TF(t) = (Number of times term t appears in a document) / (Total number of terms in the document).
def tf(total, appearances):
    return appearances / total

tf_words = extract_tf_words(ann_data)

# IDF(t) = log_e(Total number of documents / Number of documents with term t in it).
def idf(t):
    if(tf_count_files[t] is 0):
        return 0
    return n_files / tf_count_files[t]

resource_location = 'E:\\faculty\\an3\\sem2\\ln\\corpus_daa\\toponym_or_person\detection'
files = get_file_list(resource_location)
dict_file_content = get_dictionary_file_content(files)

n_files = 110

tf_count_all = {}

for word in tf_words:
    tf_count_all[word] = 0

tf_count_files = {}

for word in tf_words:
    tf_count_files[word] = 0

for (file_path, content) in dict_file_content.items():
    for word in tf_words:
        if word in content:
            tf_count_files[word]+=1

scores = list()

for (file_path, content) in dict_file_content.items():
    for word in tf_words:
        t_content = get_tokens(content)
        current_tf= tf(len(t_content), t_content.count(word))
        print("tf of", word,current_tf )
        print("tf-idf weight of", word, current_tf* idf(word))
        tf_count_all[word] += t_content.count(word)



print(tf_count_all)
print(tf_count_files)


for key in tf_count_all:
    print("idf of ", key)
    # print(tf_count_all[key]/tf_count_files[key])
    print(idf(key))


# IDF(t) = log_e(Total number of documents / Number of documents with term t in it).
