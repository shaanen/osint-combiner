from shodanobject import ShodanObject
from base import is_valid_file_name
from base import dict_clean_empty
from pathlib import Path
import json

input_file = Path('')
input_file_path = ''
print('---Shodan json converter---')
while not input_file.is_file():
    input_file_path = input('Input file (with path from project root):')
    input_file = Path(input_file_path)

str_name_output_file = ''
str_prefix_output_file = 'outputfiles/shodan/'
while not is_valid_file_name(str_name_output_file):
    str_name_output_file = input('Output file:' + str_prefix_output_file)
str_path_output_file = str_prefix_output_file + str_name_output_file

shodan = ShodanObject()
with open(str_path_output_file, 'w') as output_file:
    for str_banner in input_file.open():
        banner = dict_clean_empty(json.loads(str_banner))
        shodan.to_es_convert(shodan, banner)
        output_file.write(json.dumps(banner) + '\n')
print('Converted ' + input_file_path + ' to ' + output_file.name)
