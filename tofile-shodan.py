#!/usr/bin/env python3
from shodanfunctions import *
from base import get_queries_per_line_from_file
from base import parse_all_cidrs_from_file
from base import ask_output_file
from base import get_organizations_from_csv
from base import ask_continue
from base import get_user_boolean
import os.path

choice = get_input_choice()
should_convert = get_user_boolean('Also convert to es? y/n')
queries = set()
str_path_output_file = ''
if choice is not 3:
    str_path_output_file = ask_output_file('outputfiles/shodan/')

# 1= console queries input
if choice is 1:
    queries = get_user_input_console_queries()
    to_file_shodan(queries, str_path_output_file, should_convert)
# 2= CIDR file input
elif choice is 2:
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input CIDR file:')
    queries = ['net:' + s for s in parse_all_cidrs_from_file(input_file_path)]
    to_file_shodan(queries, str_path_output_file, should_convert)
# 3= CSV file input
elif choice is 3:
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
        queries = ['net:' + s for s in cidrs]
        print(name + ' [' + str(count) + '/' + str(len(organizations)) + ']...')
        if should_convert:
            str_path_output_file = 'outputfiles/shodan/shodan-' + name + '-converted.json'
        else:
            str_path_output_file = 'outputfiles/shodan/shodan-' + name + '.json'
        to_file_shodan(queries, str_path_output_file, should_convert)
# 4= query file input
elif choice is 4:
    input_file_path = ''
    print('Query files should contain 1 Shodan query per line.')
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input query file:')
    queries = get_queries_per_line_from_file(input_file_path)
    print('The following Shodan queries will be executed:')
    print("\n".join(queries))
    ask_continue()
    to_file_shodan(queries, str_path_output_file, should_convert)
