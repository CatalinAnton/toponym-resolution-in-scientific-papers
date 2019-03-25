import nltk

import p1_file_management
import p2_paragraph_splitter
import p3_sentence_splitter
import p4_tokenizer
import p5_pos_tagger
import p6_nnp_filter
import w5_lesk_algorithm
import json

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')

nr_sentences = 0
simple_tokens = 0
all_tokens = 0
master_list_of_dictionaries_word = []
index_words_added = 0
count_location = 0
count_person = 0
count_organization = 0

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

    from nltk.tokenize import RegexpTokenizer

    tokenizer = RegexpTokenizer(r'\w+')
    aux = tokenizer.tokenize(paragraph)
    simple_tokens += len(aux)

    aux = p4_tokenizer.get_tokens(paragraph)

    all_tokens += len(aux)

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
            nr_sentences +=1
            nerd = nltk.ne_chunk(sentence_pos_tagged)
            str_nerd = str(nerd)
            count_location += str_nerd.count("LOCATION")
            count_location += str_nerd.count("GPE")
            count_person += str_nerd.count("PERSON")
            count_organization +=str_nerd.count("ORGANIZATION")

            print(nerd)
            for t in nerd:
                if "LOCATION" in t:
                    count_location += 1
                if "PERSON" in t:
                    count_person += 1
            # identify the sense of nouns (NNP) in the sentences
            for tag in sentence_pos_tagged:
                if 'NNP' in tag[1]:
                    word = tag[0]
                    if word != None:
                        best_sense_word = w5_lesk_algorithm.lesk_algorithm(word, sentence)
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


print("nr sentences", nr_sentences)
print("tokens with no punctuation", simple_tokens)
print("all tokens", all_tokens)




# tagged = p4_tokenizer.get_tokens("Mars is a hostile planet.")
# pos_tagged = p5_pos_tagger.pos_tag(tagged)
#
# out = nltk.ne_chunk(pos_tagged)
# print(out)

print("location entities:",count_location)
print("person entities:", count_person)
print("organiztion entities:", count_organization)