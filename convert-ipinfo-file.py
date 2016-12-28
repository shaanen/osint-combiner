from ipinfoobject import IpInfoObject
from base import is_valid_file_name
from base import dict_clean_empty
from pathlib import Path
import json

input_file = Path('')
input_file_path = ''
print('---IpInfo json converter---')
while not input_file.is_file():
    input_file_path = input('Input file (with path from project root):')
    input_file = Path(input_file_path)

output_file_name = ''
output_file_path_prefix = 'outputfiles/ipinfo/'
while not is_valid_file_name(output_file_name):
    output_file_name = input('Output file:' + output_file_path_prefix)
output_file_path = output_file_path_prefix + output_file_name

ipinfo = IpInfoObject
with open(output_file_path, 'w') as output_file:
    for str_banner in input_file.open():
        banner = dict_clean_empty(json.loads(str_banner))
        ipinfo.to_es_convert(ipinfo, banner)
        output_file.write(json.dumps(banner) + '\n')
print('Converted ' + input_file_path + ' to ' + output_file_path)
