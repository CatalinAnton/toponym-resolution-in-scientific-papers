# RUN THIS BEFORE STARTING THE APPLICATION
# cd stanford-corenlp-full-2018-10-05
# java -mx4g -cp "*;stanford-corenlp-full-2017-06-09/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000

import os

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

java_path = "C:\Program Files\Java\jdk1.8.0_201\\bin\java.exe"
os.environ['JAVAHOME'] = java_path

stanford_classifier = 'C:\stanford-ner-2018-10-16\classifiers\english.muc.7class.distsim.crf.ser.gz'
stanford_ner_path = 'C:\stanford-ner-2018-10-16\stanford-ner.jar'

import p1_file_management
import p1_file_management
import p2_paragraph_splitter
import p3_sentence_splitter
import p4_tokenizer
import p5_pos_tagger
import p6_nnp_filter
import w5_lesk_algorithm
import w7_sentiments_analysis
import utils

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

NERtagger = StanfordNERTagger(stanford_classifier,
                              stanford_ner_path,
                              encoding='utf-8')

list_of_dictionaries_word_for_lesk = []
########################
# 1. getting the files #
files = p1_file_management.get_file_list(p1_file_management.resource_location)
dict_file_content = p1_file_management.get_dictionary_file_content(files)

output_sentences = list()
#############################
# 2. getting the paragraphs #
statistics_file_index_id = 0
for (file_path, content) in dict_file_content.items():
    # content = w9_anaphora_resolution.get_processed_text(content)
    # print(content)

    print('Processing -> ' + str(file_path))
    # statistics
    statistics_file_index_id += 1
    statistics_total_nr_sentences = 0
    statistics_tokens_including_punctuation = 0
    statistics_tokens_excluding_punctuation = len(utils.get_set_of_words_from_sentence(content))
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

    # paragraph_list = p2_paragraph_splitter.get_paragraphs(content)
    # for paragraph in paragraph_list:
    # TODO break down the content into paragraphs

    paragraph = content

    #############################
    # 3. getting the sentences #
    sentences = p3_sentence_splitter.get_sentences(paragraph)

    sentence_index = 0
    for sentence in sentences:
        list_of_dictionaries_word_for_ner = []
        list_of_dictionaries_word_for_lesk = []
        index_words_added_id_for_lesk = 0
        index_words_added_id_for_ner = 0
        dict_sentence_for_lesk = {'SentenceAnalized': sentence}
        dict_sentence_for_ner = {'SentenceAnalized': sentence}
        statistics_total_nr_sentences += 1

        ###################
        # 4. tokenization #
        sentence_tokenized = p4_tokenizer.get_tokens(sentence)
        statistics_tokens_including_punctuation += len(sentence_tokenized)

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

        dict_sentence_for_lesk['Words'] = list_of_dictionaries_word_for_lesk
        master_dict_for_lesk.append(dict_sentence_for_lesk)
        dict_sentence_for_ner['Words'] = list_of_dictionaries_word_for_ner
        master_dict_for_ner.append(dict_sentence_for_ner)

        statistics_nr_of_annotated_tokens += index_words_added_id_for_ner
        sentence_index += 1
        print('Finished ' + str(sentence_index) + ' sentences')
        # break after classifing the first 300 words
        if statistics_nr_of_annotated_tokens >= 300:
            break

    ##########################
    # W7. Sentiment analysis #
    c_pos, c_neg, c_neut = w7_sentiments_analysis.sentiment_alg(sentences)

    filename = p1_file_management.get_filename(file_path)
    p1_file_management.write_to_output_file_json('output_lesk/lesk_' + filename + '.json', master_dict_for_lesk)

    filename = p1_file_management.get_filename(file_path)
    p1_file_management.write_to_output_file_json('output_ner/ner_' + filename + '.json',
                                                 master_dict_for_ner)

    dict_master_statistics = {'FileId': statistics_file_index_id,
                              'NrOfSentences': statistics_total_nr_sentences,
                              'NrOfTokensIncludingPunctuation': statistics_tokens_including_punctuation,
                              'NrOfTokensExcludingPunctuation': statistics_tokens_excluding_punctuation,
                              'NrOfAnnotatedTokens': statistics_nr_of_annotated_tokens,
                              '#Location': statistics_nr_entities_location,
                              '#Person': statistics_nr_entities_person,
                              '#Organization': statistics_nr_entities_organization,
                              '#Money': statistics_nr_entities_money,
                              '#Percent': statistics_nr_entities_percent,
                              '#Date': statistics_nr_entities_date,
                              '#Time': statistics_nr_entities_time,
                              'NrOfPositiveSentiments': c_pos,
                              'NrOfNegativeSentiments': c_neg,
                              'NrOfNeutralSentiments': c_neut}

    filename = p1_file_management.get_filename(file_path)
    p1_file_management.write_to_output_file_json('output_statistics/statistics_' + filename + '.json',
                                                 dict_master_statistics)

    print('Finished -> ' + str(file_path))
    # break after reading the first file -> just for testing ;)
    break
