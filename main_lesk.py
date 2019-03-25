import p1_file_management
import p2_paragraph_splitter
import p3_sentence_splitter
import p4_tokenizer
import p5_pos_tagger
import p6_nnp_filter
import w6_lesk_algorithm
import json

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

master_list_of_dictionaries_word = []
index_words_added = 0

########################
# 1. getting the files #
files = p1_file_management.get_file_list(p1_file_management.resource_location)
dict_file_content = p1_file_management.get_dictionary_file_content(files)

output_sentences = list()
#############################
# 2. getting the paragraphs #
for (file_path, content) in dict_file_content.items():
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

            ###################################
            # W6. Word Sense Disambiguisation #
            senses = list()

            # identify the sense of nouns (NNP) in the sentences
            for tag in sentence_pos_tagged:
                if 'NNP' in tag[1]:
                    word = tag[0]
                    if word != None:
                        best_sense_word = w6_lesk_algorithm.lesk_algorithm(word, sentence)
                        if best_sense_word:
                            dict_master_word = {}
                            dict_master_word['id'] = index_words_added
                            dict_master_word['sentence'] = sentence
                            dict_master_word['wordProcessed'] = word
                            dict_master_word['senseFoundByLesk'] = best_sense_word
                            master_list_of_dictionaries_word.append(dict_master_word)
                            index_words_added += 1

                            output_sentences.append((word, best_sense_word))

    # break after reading the first file -> just for testing ;)
    break

jsoned = json.dumps(master_list_of_dictionaries_word)


with open('output_lesk/output_lesk.json', 'w') as outfile:
    json.dump(master_list_of_dictionaries_word, outfile, indent=4)