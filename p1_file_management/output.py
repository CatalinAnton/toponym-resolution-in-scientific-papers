output_location = '.\\output\\'


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
