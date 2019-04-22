import p3_sentence_splitter
import w9_anaphora_resolution


def anaphora_resolution_sentences(sentences):
    ###########################
    # W9. anaphora resolution #
    print('[Anaphora resolution] Initial text')
    for sentence in sentences:
        print(sentence)
    print()
    for sentence_index in range(0, len(sentences)):
        sentence_group_list = sentences[sentence_index: sentence_index + 5]  # RANGE
        sentence_group_string = ''
        for sentence_item in sentence_group_list:
            sentence_group_string += ' ' + sentence_item
        processed_sentence_group_string = w9_anaphora_resolution.get_processed_text(sentence_group_string)
        processed_sentence_group_list = p3_sentence_splitter.get_sentences(processed_sentence_group_string)

        for processed_item_index in range(0, len(processed_sentence_group_list)):
            processed_item = processed_sentence_group_list[processed_item_index]
            sentences[sentence_index + processed_item_index] = processed_item

        sentence_group_list = sentences[sentence_index: sentence_index + 5]
    print('[Anaphora resolution] Processed text')
    for sentence in sentences:
        print(sentence)
    print()
