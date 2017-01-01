#!/usr/bin/env python3
from shodanobject import ShodanObject
from base import parse_all_cidrs_from_file
from base import ask_output_file
import os.path


shodan = ShodanObject()
str_path_output_file = ask_output_file('outputfiles/shodan/')
choice = shodan.get_input_choice(shodan)

queries = set()
# 1= console input
if choice is 1:
    queries = shodan.get_user_input_queries()
# 2= CIDR file input
elif choice is 2:
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input file:')
    queries = ['net:' + s for s in parse_all_cidrs_from_file(input_file_path)]
if queries != set():
    shodan.to_file_shodan(shodan, queries, str_path_output_file)
