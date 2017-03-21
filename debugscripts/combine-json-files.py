#!/usr/bin/env python3
import
import argparse
import time
import json
import sys
import os

os.chdir(sys.path[0])

parser = argparse.ArgumentParser()
parser.add_argument("input", type=argparse.FileType('r'), nargs='+', help="The input files to be combined.")
parser.add_argument("-o", "--output", default="output.json", help="the file where the results will be stored "
                                                                  "(default: output.json)")
args = parser.parse_args()
path_input_file = args.input
input_files = args.input
output_file = args.output
if len(input_files) < 2:
    raise argparse.ArgumentTypeError("Need at least 2 files to combine.")
if os.path.isfile(output_file):
    msg = "{0} already exists.".format(output_file)
    raise argparse.ArgumentTypeError(msg)

t = TimeTracker()
with open(output_file, 'w') as outfile:
    for input_file in input_files:
        print('Working on ' + input_file.name + '...')
        time.sleep(1)
        with input_file as infile:
            for str_banner in infile:
                if str_banner != "":
                    outfile.write(str_banner)
print('done. Files combined in {0}'.format(output_file))
t.print_statistics()
