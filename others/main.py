import p1_file_management
import p2_paragraph_splitter
import p3_sentence_splitter
import p4_tokenizer
import p5_pos_tagger
import p6_nnp_filter

from nltk.wsd import lesk

from others.text_processing import *

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

########################
# 1. getting the files #
files = p1_file_management.get_file_list(p1_file_management.resource_location)
dict_file_content = p1_file_management.get_dictionary_file_content(files)

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
            print(sentence)

    # break after reading the first file -> just for testing ;)
    break