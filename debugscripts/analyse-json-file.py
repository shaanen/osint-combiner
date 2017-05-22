#!/usr/bin/env python3
# Script for printing and counting presence of specific JSON fields from given file
import json
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("input", help="the input file")
parser.add_argument("fieldname", help="Field name (root level)")
parser.add_argument("-s", "--silent", help="Don't print the found fields", action="store_true")
args = parser.parse_args()
if not Path(args.input).is_file():
    msg = "{0} is not an existing file".format(args.input)
    raise argparse.ArgumentTypeError(msg)

input_file = Path(args.input)

total_count = 0
present_count = 0
for element in input_file.open():
    total_count += 1
    json_element = json.loads(element)
    try:
        # print JSON element(s), if present
        if not args.silent:
            print(str(json_element[args.fieldname]))
        present_count += 1
    except KeyError:
        pass
# print statistics
print('Given field: ' + args.fieldname)
print('Given field present in: ' + str(present_count) + '/' + str(total_count) + 'total')
print('Given field missing: ' + str(total_count - present_count))
