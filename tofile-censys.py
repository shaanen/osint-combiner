#!/usr/bin/env python3
from censysobject import CensysObject
from base import get_cidr_from_user_input
from base import ask_output_file
from base import ask_input_file
from base import parse_all_cidrs_from_file
from netaddr import IPNetwork

censys = CensysObject()
str_path_output_file = ask_output_file('outputfiles/censys/')
choice = censys.get_input_choice(censys)

# 1= CIDR input
if choice is 1:
    cidr = get_cidr_from_user_input()
    query = censys.prepare_ip_or_cidr_query(censys, cidr)
    censys.to_file(censys, query, str_path_output_file)
# 2= ASN input
elif choice is 2:
    asn = censys.get_user_input_asn(censys)
    query = censys.prepare_asn_query(censys, asn)
    censys.to_file(censys, query, str_path_output_file)
# 3= CIDR file input
elif choice is 3:
    input_file = ask_input_file()
    set_cidrs = parse_all_cidrs_from_file(str(input_file))
    for cidr in set_cidrs:
        query = censys.prepare_ip_or_cidr_query(censys, IPNetwork(cidr))
        censys.to_file(censys, query, str_path_output_file)
