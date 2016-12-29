from ipinfoobject import IpInfoObject
from netaddr import IPNetwork
from base import get_cidr_from_user_input
from base import parse_all_cidrs_from_file
from base import es_get_distinct_ips
from base import is_valid_file_name
from base import is_valid_es_index_name
import os

ipinfo = IpInfoObject()
choice = ipinfo.get_input_choice(ipinfo)
cidrs = set()

str_name_output_file = ''
str_prefix_output_file = 'outputfiles/ipinfo/'
while not is_valid_file_name(str_name_output_file):
    str_name_output_file = input('Output file:' + str_prefix_output_file)
str_path_output_file = str_prefix_output_file + str_name_output_file

# 1= console input
if choice is 1:
    ipinfo.cidr_to_ipinfo(IPNetwork(get_cidr_from_user_input()), str_path_output_file)
# 2= CIDR file input
elif choice is 2:
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input file:')
    cidrs = parse_all_cidrs_from_file(input_file_path)
    print(cidrs, sep='\n')
    for cidr in cidrs:
        print('--Starting with CIDR: ' + cidr + ' (' + (str(cidrs.index(cidr) + 1)) + '/' + str(len(cidrs)) + ')--')
        ipinfo.cidr_to_ipinfo(IPNetwork(cidr), str_path_output_file)
# 3= Elasticsearch Input
elif choice is 3:
    str_input_es_index_name = ''
    while not is_valid_es_index_name(str_input_es_index_name):
        str_input_es_index_name = input("input:")
    IPs = es_get_distinct_ips(str_input_es_index_name)
    ipinfo.cidr_to_ipinfo(IPs, str_path_output_file)
