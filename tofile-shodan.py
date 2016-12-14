from base import shodan_get_user_input_queries
from base import to_file_shodan
from base import parse_all_cidrs_from_file
from base import is_valid_file_name
import os.path


output_file = ''
while not is_valid_file_name(output_file):
    output_file = input('Output filename:')
output_file_path = 'outputfiles/shodan/' + output_file


def get_choice():
    items = {'1': 'console_input', '2': 'cidr_file_input'}
    nr = '0'
    while nr not in items:
        nr = input("Console input[1] or CIDR file input[2]?")
    return nr

choice = get_choice()
queries = set()
if choice is '1':
    queries = shodan_get_user_input_queries()
elif choice is '2':
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input file:')
    queries = ['net:' + s for s in parse_all_cidrs_from_file(input_file_path)]
if queries != set():
    to_file_shodan(queries, output_file_path)
