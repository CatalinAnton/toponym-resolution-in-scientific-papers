def get_filename(file_path):
    file_path_splitted = file_path.split('\\')
    filename = file_path_splitted[len(file_path_splitted) - 1]
    return filename