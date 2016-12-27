from shodanobject import ShodanObject
from base import is_valid_file_name
from pathlib import Path


input_file = Path('')
input_file_path = ''
print('---Shodan json converter---')
while not input_file.is_file():
    input_file_path = input('Input file (with path from project root):')
    input_file = Path(input_file_path)

output_file_name = ''
output_file_path_prefix = 'outputfiles/shodan/'
while not is_valid_file_name(output_file_name):
    output_file_name = input('Output file:' + output_file_path_prefix)
path_output_file = output_file_path_prefix + output_file_name

shodan = ShodanObject()
with open(path_output_file, 'w') as output_file:
    for banner in input_file.open():
        output_file.write(shodan.shodan_to_es_convert(shodan, banner) + '\n')
print('Converted ' + input_file_path + ' to ' + output_file.name)
