#!/usr/bin/env python3
from censysobject import CensysObject
from base import get_cidr_from_user_input
from base import ask_output_file
from base import ask_input_file
from base import parse_all_cidrs_from_file
from base import get_user_boolean
from base import get_organizations_from_csv
from base import ask_continue
from netaddr import IPNetwork
import os.path

censys = CensysObject()
choice = censys.get_input_choice(censys)
str_path_output_file = ''
if choice is 5:
    str_path_output_file = ask_output_file('outputfiles/censys/')
should_convert = get_user_boolean('Also convert to es? y/n')

# 1=Console CIDR input
if choice is 1:
    cidr = get_cidr_from_user_input()
    query = censys.prepare_ip_or_cidr_query(censys, cidr)
    censys.to_file(censys, query, str_path_output_file, should_convert)
# 2=Console ASN input
elif choice is 2:
    asn = censys.get_user_input_asn(censys)
    query = censys.prepare_asn_query(censys, asn)
    censys.to_file(censys, query, str_path_output_file, should_convert)
# 3= CIDR file input
elif choice is 3:
    input_file = ask_input_file()
    set_cidrs = parse_all_cidrs_from_file(str(input_file))
    for cidr in set_cidrs:
        query = censys.prepare_ip_or_cidr_query(censys, IPNetwork(cidr))
        censys.to_file(censys, query, str_path_output_file, should_convert)
# 4=Console Custom WHERE query
elif choice is 4:
    query = censys.prepare_custom_query(censys, censys.sql_get_custom_query_from_user(censys))
    censys.to_file(censys, query, str_path_output_file, should_convert)
# 5= CSV file input
elif choice is 5:
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input CSV file:')
    organizations = get_organizations_from_csv(input_file_path)
    print(organizations.keys())
    print(str(len(organizations)) + ' organizations found.')
    ask_continue()
    count = 0
    for name, cidrs in organizations.items():
        count += 1
        print(name + ' [' + str(count) + '/' + str(len(organizations)) + ']...')
        query = censys.prepare_ip_or_cidr_query(censys, cidrs)
        if should_convert:
            str_path_output_file = 'outputfiles/censys/censys-' + name + '-converted.json'
        else:
            str_path_output_file = 'outputfiles/censys/censys-' + name + '.json'
        censys.to_file(censys, query, str_path_output_file, should_convert)

