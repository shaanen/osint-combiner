#!/usr/bin/env python3
from timetracker import TimeTracker
from pathlib import Path
import argparse
import json
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument("input", help="the input file or directory of files to be converted")
args = parser.parse_args()
path_input_file = args.input
if not Path(path_input_file).is_file():
    msg = "{0} is not an existing file".format(args.input)
    raise argparse.ArgumentTypeError(msg)

t = TimeTracker()
ips = set()
for str_banner in Path(path_input_file).open('r', encoding='utf-8'):
    if str_banner != '\n':
        try:
            ips.add(json.loads(str_banner)['ip'])
        except json.decoder.JSONDecodeError as e:
            print(e.args)
            print('Malformed json: ' + str_banner)
print(str(len(ips)) + ' distinct IPs in ' + path_input_file)
t.print_statistics()

