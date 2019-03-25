# named entity recognition
import p1_file_management
from p1_file_management.output import write_to_output_file_json
from p1_file_management.file_path import get_filename
import p2_paragraph_splitter
import p3_sentence_splitter
import p4_tokenizer
import p5_pos_tagger
import p6_nnp_filter
import w6_lesk_algorithm

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')


import os

java_path = "C:\Program Files\Java\jdk1.8.0_201\\bin\java.exe"
os.environ['JAVAHOME'] = java_path

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

stanford_classifier = 'C:\stanford-ner-2018-10-16\classifiers\english.all.3class.distsim.crf.ser.gz'
stanford_ner_path = 'C:\stanford-ner-2018-10-16\stanford-ner.jar'

NERtagger = StanfordNERTagger(stanford_classifier,
                              stanford_ner_path,
                              encoding='utf-8')

########################
# 1. getting the files #
files = p1_file_management.get_file_list(p1_file_management.resource_location)
dict_file_content = p1_file_management.get_dictionary_file_content(files)

output_sentences = list()
#############################
# 2. getting the paragraphs #

for (file_path, content) in dict_file_content.items():
    master_list_of_dictionaries_word = []
    index_words_added = 0
    # paragraph_list = p2_paragraph_splitter.get_paragraphs(content)
    # for paragraph in paragraph_list:
    # TODO break down the content into paragraphs

    paragraph = content

    #############################
    # 3. getting the sentences #
    sentences = p3_sentence_splitter.get_sentences(paragraph)
    for sentence in sentences:

        ###################
        # 4. tokenization #
        sentence_tokenized = p4_tokenizer.get_tokens(sentence)

        ################################
        # 5. pos tagging the sentences #
        sentence_pos_tagged = p5_pos_tagger.pos_tag(sentence_tokenized)

        ##########################
        # 6. NNP sentence filter #
        if (p6_nnp_filter.is_NNP_sentence(sentence_pos_tagged)):
            ##########
            # 8. NER #
            classified_text_list = NERtagger.tag(sentence_tokenized)
            # print(classified_text_list)
            for element in classified_text_list:
                dict_master_word = {}
                dict_master_word['id'] = index_words_added
                dict_master_word['word'] = element[0]
                dict_master_word['classModel'] = element[1]
                master_list_of_dictionaries_word.append(dict_master_word)
                index_words_added += 1
        # break after classifing the first 100 words
        if (index_words_added >= 100):
            break
        print(index_words_added)

    filename = get_filename(file_path)
    write_to_output_file_json('output_ner/ner_' + filename + '.json', master_list_of_dictionaries_word)

    # break after reading the first file -> just for testing ;)
    break
# jsoned = json.dumps(master_list_of_dictionaries_word)
