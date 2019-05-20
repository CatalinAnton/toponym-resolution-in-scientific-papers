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


def get_dictionary_geo_names(geo_names_path):
    with open(geo_names_path, 'r', encoding='utf8', errors='ignore') as geo_names_file:
        line = geo_names_file.readline()
        cnt = 1
        dictionary_geo_names = {}
        while line:
            line_splitted = line.strip().split('\t')
            toponym = line_splitted[1]
            location = line_splitted[17]
            latitude = line_splitted[4]
            longitude = line_splitted[5]
            dictionary_geo_names[toponym] = {"location": location, "latitude": latitude, "longitude": longitude}
            line = geo_names_file.readline()
            if(cnt % 1000000 == 0):
                print('Created', cnt, 'keys in the geo names dictionary')
            cnt += 1
        return dictionary_geo_names