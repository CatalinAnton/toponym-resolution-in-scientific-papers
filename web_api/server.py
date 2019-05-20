# RUN THIS BEFORE STARTING THE SERVER
# cd stanford-corenlp-full-2018-10-05
# java -mx4g -cp "*;stanford-corenlp-full-2017-06-09/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000

import p1_file_management
import p3_sentence_splitter
import p4_tokenizer
import p5_pos_tagger
import p6_nnp_filter
import w5_lesk_algorithm
import utils

import os
from nltk.tag import StanfordNERTagger

import nltk

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

java_path = "C:\Program Files\Java\jdk1.8.0_201\\bin\java.exe"
os.environ['JAVAHOME'] = java_path

stanford_classifier = 'C:\stanford-ner-2018-10-16\classifiers\english.muc.7class.distsim.crf.ser.gz'
stanford_ner_path = 'C:\stanford-ner-2018-10-16\stanford-ner.jar'

NERtagger = StanfordNERTagger(stanford_classifier,
                              stanford_ner_path,
                              encoding='utf-8')

import sys

print(sys.maxsize)

####################################
# Creating dictionary of geo names #
dictionary_geo_names = p1_file_management.get_dictionary_geo_names('..\\resources\\geo_names\\allCountries.txt')

import json
import flask_cors
from flask import Flask, request
from flask_cors import cross_origin

app = Flask(__name__)
cors = flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/text', methods=['POST'])
@cross_origin()
def post_text():
    if request.method == 'POST':
        data = request.json
        print(data)
        raw_text = data["text"]

        # toponyms should have a python dictionary or a json object already
        toponyms = extract_toponyms(raw_text)
        json_toponyms = json.dumps(toponyms)
        return json_toponyms


def extract_toponyms(raw_text):
    result = None

    statistics_total_nr_sentences = 0
    statistics_tokens_including_punctuation = 0
    statistics_tokens_excluding_punctuation = len(utils.get_set_of_words_from_sentence(raw_text))
    statistics_nr_of_annotated_tokens = 0

    statistics_nr_entities_location = 0
    statistics_nr_entities_person = 0
    statistics_nr_entities_organization = 0
    statistics_nr_entities_money = 0
    statistics_nr_entities_percent = 0
    statistics_nr_entities_date = 0
    statistics_nr_entities_time = 0

    master_dict_for_lesk = []
    master_dict_for_ner = []
    master_dict_FINAL = []
    index_toponym_added_id_FINAL = 0

    #############################
    # 3. getting the sentences #
    sentences = p3_sentence_splitter.get_sentences(raw_text)

    sentence_index = 0
    for sentence in sentences:
        list_of_dictionaries_word_for_ner = []
        list_of_dictionaries_word_for_lesk = []
        list_of_dictionaries_word_FINAL = []
        index_words_added_id_for_lesk = 0
        index_words_added_id_for_ner = 0
        dict_sentence_for_lesk = {'SentenceAnalized': sentence}
        dict_sentence_for_ner = {'SentenceAnalized': sentence}
        dict_sentence_FINAL = {'sentence': sentence}

        ###################
        # 4. tokenization #
        sentence_tokenized = p4_tokenizer.get_tokens(sentence)

        ################################
        # 5. pos tagging the sentences #
        sentence_pos_tagged = p5_pos_tagger.pos_tag(sentence_tokenized)

        ##########################
        # 6. NNP sentence filter #
        if p6_nnp_filter.is_NNP_sentence(sentence_pos_tagged):

            ###################################
            # W5. Word Sense Disambiguisation #
            senses = list()
            # identify the sense of nouns (NNP) in the sentences
            for tag in sentence_pos_tagged:
                if 'NNP' in tag[1]:
                    word = tag[0]
                    if word != None:
                        best_sense_word = w5_lesk_algorithm.lesk_algorithm(word, sentence)
                        if best_sense_word:
                            dict_word_for_lesk = {}
                            dict_word_for_lesk['WordId'] = index_words_added_id_for_lesk
                            dict_word_for_lesk['Word'] = word
                            dict_word_for_lesk['SenseFoundByLesk'] = best_sense_word
                            list_of_dictionaries_word_for_lesk.append(dict_word_for_lesk)
                            index_words_added_id_for_lesk += 1
            # end of w5

            ################################
            # W6. Named-entity recognition #
            classified_text_list = NERtagger.tag(sentence_tokenized)
            # print(classified_text_list)
            for element in classified_text_list:
                dict_word = {'WordId': index_words_added_id_for_ner,
                             'Word': element[0],
                             'ClassModel': element[1]}
                if element[1] == 'LOCATION':
                    statistics_nr_entities_location += 1
                elif element[1] == 'PERSON':
                    statistics_nr_entities_person += 1
                elif element[1] == 'ORGANIZATION':
                    statistics_nr_entities_organization += 1
                elif element[1] == 'MONEY':
                    statistics_nr_entities_money += 1
                elif element[1] == 'PERCENT':
                    statistics_nr_entities_percent += 1
                elif element[1] == 'DATE':
                    statistics_nr_entities_date += 1
                elif element[1] == 'TIME':
                    statistics_nr_entities_time += 1
                list_of_dictionaries_word_for_ner.append(dict_word)
                index_words_added_id_for_ner += 1
            # end of w6

            ##################
            # W10. Validator #
            index_element = 0
            for index_element in range(0, len(classified_text_list)):
                toponym_word = ''
                found_toponym = False
                if (classified_text_list[index_element][1] == 'LOCATION'
                        and index_element + 1 < len(classified_text_list)
                        and classified_text_list[index_element + 1][1] == 'LOCATION'):
                    toponym_word = classified_text_list[index_element][0] + ' ' + \
                                   classified_text_list[index_element + 1][0]
                    found_toponym = True
                else:
                    if classified_text_list[index_element][1] == 'LOCATION' and classified_text_list[index_element - 1][
                        1] != 'LOCATION':
                        toponym_word = classified_text_list[index_element][0]
                        found_toponym = True
                if found_toponym and toponym_word in dictionary_geo_names:
                    print('Found toponym:', toponym_word)
                    dict_word = {'toponymId': index_toponym_added_id_FINAL,
                                 'toponym': toponym_word,
                                 'latitude': dictionary_geo_names[toponym_word]['latitude'],
                                 'longitude': dictionary_geo_names[toponym_word]['longitude']}
                    list_of_dictionaries_word_FINAL.append(dict_word)
                    index_toponym_added_id_FINAL += 1

        dict_sentence_for_lesk['Words'] = list_of_dictionaries_word_for_lesk
        master_dict_for_lesk.append(dict_sentence_for_lesk)
        dict_sentence_for_ner['Words'] = list_of_dictionaries_word_for_ner
        master_dict_for_ner.append(dict_sentence_for_ner)
        dict_sentence_FINAL['words'] = list_of_dictionaries_word_FINAL
        if len(dict_sentence_FINAL['words']) > 0:
            master_dict_FINAL.append(dict_sentence_FINAL)

        statistics_nr_of_annotated_tokens += index_words_added_id_for_ner
        sentence_index += 1
        print('Finished ' + str(sentence_index) + ' sentences')

    output_final = {'sentences': master_dict_FINAL}
    print('Finished')
    return output_final


app.run(host='localhost', port=8880)
