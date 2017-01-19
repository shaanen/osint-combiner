from ipinfoobject import IpInfoObject
from base import dict_clean_empty
from base import ask_input_file
from base import increment_until_new_file
import json
import os

print('---IpInfo json converter---')
input_file = ask_input_file('outputfiles/ipinfo/')
str_path_output_file = increment_until_new_file('sample_outputfiles/' +
                                                os.path.splitext(os.path.basename(str(input_file)))[0]
                                                + '-converted' + os.path.splitext(str(input_file))[1])
ipinfo = IpInfoObject
with open(str_path_output_file, 'a') as output_file:
    for str_banner in input_file.open():
        banner = dict_clean_empty(json.loads(str_banner))
        ipinfo.to_es_convert(ipinfo, banner)
        output_file.write(json.dumps(banner) + '\n')
print('Converted ' + str(input_file.as_posix()) + ' to ' + str_path_output_file)
