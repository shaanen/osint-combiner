#!/usr/bin/env python3
from shodanobject import ShodanObject
from base import parse_all_cidrs_from_file
from base import is_valid_file_name
import os.path


shodan = ShodanObject()
output_file = ''
while not is_valid_file_name(output_file):
    output_file = input('Output file:')
path_output_file = 'outputfiles/shodan/' + output_file


choice = shodan.get_input_choice(shodan)
queries = set()
if choice is 1:
    queries = shodan.get_user_input_queries()
elif choice is 2:
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input file:')
    queries = ['net:' + s for s in parse_all_cidrs_from_file(input_file_path)]
if queries != set():
    shodan.to_file_shodan(shodan, queries, path_output_file)
