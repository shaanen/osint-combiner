#!/usr/bin/env python3
import json
from pathlib import Path

# DEBUG Script for printing and counting presence of specific JSON fields from given file

total_count = 0
present_count = 0
input_file = Path('../outputfiles/shodan/test.json')
for element in input_file.open():
    total_count += 1
    json_element = json.loads(element)
    try:
        # print JSON element(s), if present
        print(str(json_element['ip']))
        present_count += 1
    except KeyError:
        pass
# print statistics
print('Given element(s) present in: ' + str(present_count) + '/' + str(total_count) + 'total')
print('Given element(s) missing: ' + str(total_count - present_count))
