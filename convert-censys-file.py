#!/usr/bin/env python3
from censysfunctions import *
from pathlib import Path
from base import dict_clean_empty
from base import increment_until_new_file
from base import create_output_directory
from base import ask_continue
import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("input", help="the input file or directory of files to be converted")
parser.add_argument("-y", "--yes", "--assume-yes", help="Automatic yes to prompts; assume \"yes\" as answer to all "
                                                        "prompts and run non-interactively.", action="store_true")
args = parser.parse_args()

print('---Censys converter---')

# A file input
if Path(args.input).is_file():
    input_file = Path(args.input)
    str_path_output_file = increment_until_new_file('converted_outputfiles/' +
                                                    os.path.splitext(os.path.basename(str(input_file)))[0]
                                                    + '-converted' + os.path.splitext(str(input_file))[1])
    with open(str_path_output_file, 'a', encoding='utf-8') as output_file:
        for str_banner in input_file.open(encoding='utf8'):
            if str_banner != '\n':
                banner = dict_clean_empty(json.loads(str_banner))
                to_es_convert(banner)
                output_file.write(json.dumps(banner) + '\n')
    print('Converted ' + str(input_file.as_posix()) + ' to ' + str_path_output_file)

# A directory input
elif os.path.isdir(args.input):
    input_directory = args.input
    files_to_convert = []
    for file in os.listdir(input_directory):
        if file.endswith(".json"):
            files_to_convert.append(file)
    print('These files will be converted: ' + str(files_to_convert))
    print('Total number of files: ' + str(len(files_to_convert)))
    if not args.yes:
        ask_continue()
    output_directory = create_output_directory(input_directory)
    counter = 0
    for input_file in files_to_convert:
        counter += 1
        str_output_file = output_directory + '/' + input_file[:-5] + '-converted.json'
        print('\r' + 'Converting ' + input_file + '[' + str(counter) + '/' + str(len(files_to_convert)) + ']..', end='')
        with open(str_output_file, 'a') as output_file:
            for str_banner in open(input_directory + '/' + input_file, 'r'):
                if str_banner != '\n':
                    banner = dict_clean_empty(json.loads(str_banner))
                    to_es_convert(banner)
                    output_file.write(json.dumps(banner) + '\n')
    print('\nConverted files written in ' + output_directory)
else:
    msg = "{0} is not an existing file or directory".format(args.input)
    raise argparse.ArgumentTypeError(msg)
