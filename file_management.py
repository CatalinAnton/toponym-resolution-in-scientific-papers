import os

resource_location = '.\\resources\\txt'
output_location = '.\\output\\'

def get_file_list(source):
    matches = []
    for root, dirnames, filenames in os.walk(source):
        for filename in filenames:
            matches.append(os.path.join(root, filename))
    return matches

def get_dictionary_file_content(files):
    dict_file_content = {}
    for file in files:
        with open(file) as f:
            content_of_file = f.read()
            dict_file_content[file] = content_of_file
    return dict_file_content

def get_filename(file_path):
    file_path_splitted = file_path.split('\\')
    filename = file_path_splitted[len(file_path_splitted) - 1]
    return filename


def write_to_output_file(filename, content):
    file_path = output_location + filename
    with open(file_path, 'w') as f:
        for line in content:
            f.write(str(line) + ' ')

def write_to_output_file_with_endl(filename, content):
    file_path = output_location + filename
    with open(file_path, 'w') as f:
        for line in content:
            f.write(str(line) + '\n')