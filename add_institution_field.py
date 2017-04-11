#!/usr/bin/env python3
# This script could be used if you want to add an 'institution' field to every converted result later on.
# This script will add a field with the organization name to every json result from given inputfile based on given CSV
# file containing IP ranges.
# This script should be used after the results are converted, when the -i flag was not already set in the converters.
from base import get_institutions_from_given_csv
from base import check_exists_input_file
from netaddr import IPAddress
from timetracker import TimeTracker
from base import check_outputfile
from pathlib import Path
import argparse
import json
import sys
import os

os.chdir(sys.path[0])

parser = argparse.ArgumentParser()
parser.add_argument("csvfile", help="CSV file containing an organization name and CIDR per row. Multiple rows with the "
                                    "same organization name will be combined.")
parser.add_argument('inputfile', help='The input file containing converted json results')
args = parser.parse_args()

check_exists_input_file(args.csvfile)
check_exists_input_file(args.inputfile)
path_output_file = args.inputfile[:-5] + '-institution.json'
check_outputfile(path_output_file)

print('---Institution field inserter---')
t = TimeTracker()
organizations = get_institutions_from_given_csv(args.csvfile)
nr_done = 0
with open(path_output_file, 'w') as outfile:
    for str_result in Path(args.inputfile).open('r', encoding='utf-8'):
        if str_result != '\n':
            try:
                result = json.loads(str_result)
                ip = IPAddress(result['ip'])
                found = False
                for name, cidrs in organizations.items():
                    if found:
                        break
                    else:
                        for cidr in cidrs:
                            if ip in cidr:
                                result['institution'] = name
                                found = True
                                break
                if 'institution' not in result:
                    result['institution'] = 'OTHER'
                outfile.write(str(json.dumps(result) + '\n'))
                nr_done += 1
                print('\r' + str(nr_done), end='')
            except json.decoder.JSONDecodeError as e:
                print(str(e))
                print('Error occurred in result: \n' + str_result)
print('\nDone. Results saved in ' + path_output_file)
t.print_statistics()
