import os

resource_location = '.\\resources\\txt'


def get_file_list(source):
    files = []
    for root, dirnames, filenames in os.walk(source):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files


def get_dictionary_file_content(files):
    dict_file_content = {}
    for file in files:
        with open(file) as f:
            content_of_file = f.read()
            dict_file_content[file] = content_of_file
    return dict_file_content


resource_location_output = '..\\output_final'

def get_file_list_output_final():
    files = []
    for root, dirnames, filenames in os.walk(resource_location_output):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files
