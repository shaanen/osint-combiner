#!/usr/bin/env python3
from shodanfunctions import *
from base import get_queries_per_line_from_file
from base import get_organizations_from_csv
from base import parse_all_cidrs_from_file
from base import ask_continue
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--convert", help="Convert immediately without storing original file.", action="store_true")
parser.add_argument("-y", "--yes", "--assume-yes", help="Automatic yes to prompts; assume \"yes\" as answer to all "
                                                        "prompts and run non-interactively.", action="store_true")
subparsers = parser.add_subparsers()
query = subparsers.add_parser('queryfile', help='Textfile containing one Shodan query per line;')
query.add_argument("inputfile", help="the input file")
query.add_argument('outputfile', help='The file where the results will be stored.')
query.set_defaults(subparser='queryfile')

cidr = subparsers.add_parser('cidrfile', help='Textfile containing CIDRs;')
cidr.add_argument("inputfile", help="the input file")
cidr.add_argument('outputfile', help='The file where the results will be stored.')
cidr.set_defaults(subparser='cidrfile')

csv = subparsers.add_parser('csvfile', help='CSV file containing an organization name and CIDR per row. Multiple rows '
                                            'with the same organization name will be combined. Every organization will '
                                            'have it\'s own output file.')
csv.add_argument("inputfile", help="the input file")
csv.set_defaults(subparser='csvfile')

args = parser.parse_args()
choice = args.subparser

if Path(args.inputfile).is_file():
    should_convert = args.convert
    queries = set()
    # CIDR file input
    if choice is 'cidrfile':
        queries = ['net:' + s for s in parse_all_cidrs_from_file(args.inputfile, args.yes)]
        to_file_shodan(queries, args.outputfile, should_convert)
    # query file input
    elif choice is 'queryfile':
        queries = get_queries_per_line_from_file(args.inputfile)
        print('The following Shodan queries will be executed:')
        print("\n".join(queries))
        if not args.yes:
            ask_continue()
        to_file_shodan(queries, args.outputfile, should_convert)
    # CSV file input
    elif choice is 'csvfile':
        organizations = get_organizations_from_csv(args.inputfile)
        print(organizations.keys())
        print(str(len(organizations)) + ' organizations found.')
        if not args.yes:
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
else:
    msg = "{0} is not an existing file".format(args.inputfile)
    raise argparse.ArgumentTypeError(msg)
