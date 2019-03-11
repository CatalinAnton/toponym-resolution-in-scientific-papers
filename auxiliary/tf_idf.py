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


tf_words = extract_tf_words(ann_data)

resource_location = 'E:\\faculty\\an3\\sem2\\ln\\corpus_daa\\toponym_or_person\detection'
files = get_file_list(resource_location)
dict_file_content = get_dictionary_file_content(files)

n_files = len(files)

tf_count_all = {}

for word in tf_words:
    tf_count_all[word] = 0

tf_count_files = {}

for word in tf_words:
    tf_count_files[word] = 0

for (file_path, content) in dict_file_content.items():

    for word in tf_words:
        t_content = get_tokens(content)
        tf_count_all[word]+=t_content.count(word)

    for word in tf_words:
        if word in content:
            tf_count_files[word]+=1

print(tf_count_all)
print(tf_count_files)
