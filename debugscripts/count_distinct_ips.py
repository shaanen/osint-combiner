# --------------------------------------------------------------------------------------------
# Copyright (c) jehama en Sjors. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#!/usr/bin/env python3

""" A script to count the distinct IP's from a JSON file."""
# imports
import argparse
import json
import os
import sys
from pathlib import Path
from timetracker import TimeTracker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add arguments from the command line.
parser = argparse.ArgumentParser()
parser.add_argument(
    "input", help="the input file or directory of files to be converted")
args = parser.parse_args()
path_input_file = args.input

# Check if the given file exists.
if not Path(path_input_file).is_file():
    msg = "{0} is not an existing file".format(args.input)
    raise argparse.ArgumentTypeError(msg)

t = TimeTracker()
ips = set()
# Loop over the JSON dataset and and count the IP's.
for str_banner in Path(path_input_file).open(encoding='utf-8'):
    if str_banner != '\n':
        ips.add(json.loads(str_banner)['ip'])
# Print the amount of IP's and some statistics.
print(str(len(ips)) + ' distinct IPs in ' + path_input_file)
t.print_statistics()
