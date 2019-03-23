import p1_file_management
import p2_paragraph_splitter
import p3_sentence_splitter
import p4_tokenizer
import p5_pos_tagger
import p6_nnp_filter

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
    break;

# TODO
#   https://profs.info.uaic.ro/~daniela.gifu/nle.html
#   A. Modulul final va returna output-ul sub forma unui fisier JSON/XML
#   B. Word Sense Disambiguation - LESK ALGORITHM
#      lesk algorithm + wordnet
#      Ex: intersectia sensurilor (e.g. pine cone) -> vedem lemme-le celor doua cuvinte
#          si apoi realizam intersectia sensurilor lor
#          Noun
#          pine (countable and uncountable, plural pines)
#               1. (countable, uncountable) Any coniferous tree of the genus Pinus.
#                   The northern slopes were covered mainly in pine.
#               2. (countable) Any tree (usually coniferous) which resembles a member of this genus in some respect.
#               3. (uncountable) The wood of this tree.
#               4. (archaic except South Africa) A pineapple.
#         cone (plural cones)
#               1. (geometry) A surface of revolution formed by rotating a segment of a line around another
#                  line that intersects the first line.
#               2. (geometry) A solid of revolution formed by rotating a triangle around one of its altitudes.
#               3. (topology) A space formed by taking the direct product of a given space with a closed
#                  interval and identifying all of one end to a point.
#               4. Anything shaped like a cone.[1]
#               5. The fruit of a conifer.[1]
#         Dupa ce am preluat sensurile intersectam cuvintele (esentiale, nu conjunctii
#         si prepozitii - aceste nu ne spun nimic despre sens) si vedem daca exista
#         cuvinte comune. Daca exista inseamna ca am aflat sensul grupului de cuvinte :D
#         e.g. sensul 1 al cuvantului pine contine cuvantul conifer, iar
#              sensul 5 al cuvantului cone contine cuvantul conifer
#   C. de adaugat pe profesoara la folderul de contul de GDrive daniela.gifu33@gmail.com
