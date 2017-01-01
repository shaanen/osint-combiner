#!/usr/bin/env python3
from shodanobject import ShodanObject
from base import dict_clean_empty
from base import ask_input_file
from base import ask_output_file
import json

print('---Shodan json converter---')
input_file = ask_input_file()
str_path_output_file = ask_output_file('outputfiles/shodan/')

shodan = ShodanObject()
with open(str_path_output_file, 'a') as output_file:
    for str_banner in input_file.open():
        banner = dict_clean_empty(json.loads(str_banner))
        shodan.to_es_convert(shodan, banner)
        output_file.write(json.dumps(banner) + '\n')
print('Converted ' + str(input_file.as_posix()) + ' to ' + str_path_output_file)
