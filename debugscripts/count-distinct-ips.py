#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from timetracker import TimeTracker
from pathlib import Path
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("input", help="the input file or directory of files to be converted")
args = parser.parse_args()
path_input_file = args.input
if not Path(path_input_file).is_file():
    msg = "{0} is not an existing file".format(args.input)
    raise argparse.ArgumentTypeError(msg)

t = TimeTracker()
ips = set()
for str_banner in Path(path_input_file).open(encoding='utf-8'):
    if str_banner != '\n':
        ips.add(json.loads(str_banner)['ip'])
print(str(len(ips)) + ' distinct IPs in ' + path_input_file)
t.print_statistics()

