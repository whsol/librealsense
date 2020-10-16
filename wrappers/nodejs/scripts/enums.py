import re
import os
import sys

ENUM_H_NAME_REGEXP = r'typedef enum (\w+)'
ENUM_H_ITEM_REGEXP = r'^[ ]*(RS2_\w+)'

ENUM_CPP_REGEXP = r'^[ ]*_FORCE_SET_ENUM\((\w+)\)'
ENUM_JS_REGEXP = r'RS2\.(RS2_\w+)'


def files_gen(path, ends):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(ends):
                yield os.path.join(root, file)


def get_first_by_regexp(line, regexp):
    res = re.findall(regexp, line)
    if res:
        return res[0]
    return ''


def get_enums_from_h_file(file_path):
    enums = []
    with open(file_path) as f:
        enum_name = ''
        for line in f:
            if not enum_name:
                enum_name = get_first_by_regexp(line, ENUM_H_NAME_REGEXP)
                continue

            enum = get_first_by_regexp(line, ENUM_H_ITEM_REGEXP)

            if enum:
                enums.append(enum)

            if bool(re.search(enum_name, line)):
                enum_name = ''

    return enums


def get_enums_from_folder(folder_path, ends, regexp):
    file_paths = files_gen(folder_path, ends)
    enums = []
    for file_path in file_paths:
        enums += get_enums_from_file(file_path, regexp)
    return enums


def get_enums_from_file(file_path, regexp):
    enums = []
    with open(file_path) as f:
        for line in f:
            enum = get_first_by_regexp(line, regexp)
            if enum:
                enums.append(enum)

    return enums


def run(include_folder_path, addon_folder_path, js_file_path):

    include_enums = get_enums_from_folder(include_folder_path, '.h', ENUM_H_ITEM_REGEXP)
    cpp_enums = get_enums_from_folder(addon_folder_path, '.cpp', ENUM_CPP_REGEXP)
    js_enums = get_enums_from_file(js_file_path, ENUM_JS_REGEXP)

    include_enums.sort()
    cpp_enums.sort()
    # js_enums.sort()

    # print(len(include_enums), len(cpp_enums), len(js_enums))
    return list(set(include_enums) - set(cpp_enums))


if __name__ == '__main__':
    (include_folder_path, addon_folder_path, js_file_path) = sys.argv[1:]

    missed = run(include_folder_path, addon_folder_path, js_file_path)
    if missed:
        sys.exit(missed)

    sys.exit()
