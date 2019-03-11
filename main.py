from file_management import *
from text_processing import *

import nltk
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

files = get_file_list(resource_location)
dict_file_content = get_dictionary_file_content(files)

for (file_path, content) in dict_file_content.items():
    ############################
    # tokenizare + pos tagging #
    ############################
    text_pos_tagged = preprocess(content)
    filename = get_filename(file_path)
    write_to_output_file_with_endl('pos_tag' + filename, text_pos_tagged)

    #########
    # lemma #
    #########
    list_lemma = get_lemmas(content)
    write_to_output_file('lemma_' + filename, list_lemma)

    language_of_file = get_language_of_text(content)
    print(filename + ' - language of file - ' + language_of_file)

    print(get_tokens(content))
    print(get_sentences(content))
    print("sentences with nnp")
    print(get_pn_sentences(content))


    # de scos hiponime si hipernime 