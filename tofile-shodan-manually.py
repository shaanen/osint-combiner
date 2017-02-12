#!/usr/bin/env python3
from shodanfunctions import *
from base import ask_output_file
from base import get_user_boolean

# Script where user can enter Shodan queries manually in the command-line
should_convert = get_user_boolean('Also convert to es? y/n')
str_path_output_file = ask_output_file('outputfiles/shodan/')
queries = get_user_input_console_queries()
to_file_shodan(queries, str_path_output_file, should_convert)

