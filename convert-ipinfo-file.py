from ipinfoobject import IpInfoObject
from base import is_valid_file_name
from base import dict_clean_empty
from base import ask_input_file
import json

print('---IpInfo json converter---')
input_file = ask_input_file()

str_name_output_file = ''
str_prefix_output_file = 'outputfiles/ipinfo/'
while not is_valid_file_name(str_name_output_file):
    str_name_output_file = input('Output file:' + str_prefix_output_file)
str_path_output_file = str_prefix_output_file + str_name_output_file

ipinfo = IpInfoObject
with open(str_path_output_file, 'w') as output_file:
    for str_banner in input_file.open():
        banner = dict_clean_empty(json.loads(str_banner))
        ipinfo.to_es_convert(ipinfo, banner)
        output_file.write(json.dumps(banner) + '\n')
print('Converted ' + input_file_path + ' to ' + str_path_output_file)
