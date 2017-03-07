#!/usr/bin/env python3
from base import get_cidr_from_user_input
from timetracker import TimeTracker
from base import get_user_boolean
from base import ask_output_file
from censysfunctions import *
import sys
import os

os.chdir(sys.path[0])

# Script where user can enter a CIDR or ASN or a Censys query manually in the command-line
str_path_output_file = ask_output_file('outputfiles/censys/')
should_convert = get_user_boolean('Also convert to es? y/n')
choice = get_input_choice()
t = TimeTracker()

# Console CIDR input
if choice is 1:
    cidr = get_cidr_from_user_input()
    query = prepare_cidrs_query(cidr)
    to_file(query, str_path_output_file, should_convert)
# Console ASN input
elif choice is 2:
    asn = get_user_input_asn()
    query = prepare_asn_query(asn)
    to_file(query, str_path_output_file, should_convert)
# Console Custom WHERE query
elif choice is 3:
    query = prepare_custom_query(sql_get_custom_query_from_user())
    to_file(query, str_path_output_file, should_convert)
t.print_statistics()