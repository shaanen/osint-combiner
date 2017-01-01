#!/usr/bin/env python3
from censysobject import CensysObject
from base import dict_clean_empty
from base import ask_input_file
from base import ask_output_file
import json

print('---Censys json converter---')
input_file = ask_input_file()
str_path_output_file = ask_output_file('outputfiles/censys/')

censys = CensysObject
with open(str_path_output_file, 'a', encoding='utf-8') as output_file:
    for str_banner in input_file.open(encoding='utf8'):
        banner = dict_clean_empty(json.loads(str_banner))
        censys.to_es_convert(censys, banner)
        output_file.write(json.dumps(banner) + '\n')
print('Converted ' + str(input_file.as_posix()) + ' to ' + str_path_output_file)

