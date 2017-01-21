#!/usr/bin/env python3
import json
from pathlib import Path

# DEBUG Script for printing and counting presence of specific JSON fields from given file
list_of_protocols = []
total_count = 0
present_count = 0
input_file = Path('inputfiles/mapping.json')
for element in input_file.open():
    total_count += 1
    json_element = json.loads(element)
    for key in json_element['properties']:
        print (str(key) + ' | ' + str(len(str(json_element['properties'][key]))))
        #protocol = json_element['censys'][str_protocol]
        #print(str_protocol + ' | ' + str(len(str(protocol))))
        #list_of_protocols.append()
        #list_of_protocols[str(len(str(protocol)))] = str_protocol
#print(str(sorted(list_of_protocols)))
    # print(type(json_element['properties']))
    # try:
    #     # print JSON element(s), if present
    #     print(str(json_element['ip']))
    #     present_count += 1
    # except KeyError:
    #     pass
# print statistics
print('-----------')
print('Given element(s) present in: ' + str(present_count) + '/' + str(total_count) + 'total')
print('Given element(s) missing: ' + str(total_count - present_count))