# --------------------------------------------------------------------------------------------
# Copyright (c) jehama en Sjors. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#!/usr/bin/env python3

""" A script to combine JSON files."""
# imports
import argparse
import os
import sys
import time
from timetracker import TimeTracker

# Setting the working directory of the script.
os.chdir(sys.path[0])

# Add arguments from the command line.
parser = argparse.ArgumentParser()
parser.add_argument("input", type=argparse.FileType(
    "r"), nargs="+", help="The input files to be combined.")
parser.add_argument("-o", "--output", default="output.json", help="the file where the results will be stored "
                                                                  "(default: output.json)")
args = parser.parse_args()
input_files = args.input
output_file = args.output
# Check to make sure enough files have been provided.
if len(input_files) < 2:
    raise argparse.ArgumentTypeError("Need at least 2 files to combine.")
# Check to make sure there is not file with the same name as the output file.
if os.path.isfile(output_file):
    msg = "{0} already exists.".format(output_file)
    raise argparse.ArgumentTypeError(msg)

t = TimeTracker()
# The combining of a JSON files in a new file.
with open(output_file, "w") as outfile:
    for input_file in input_files:
        print("Working on " + input_file.name + "...")
        time.sleep(1)
        with input_file as infile:
            for str_banner in infile:
                if str_banner != "":
                    outfile.write(str_banner)
print("done. Files combined in {0}".format(output_file))
t.print_statistics()
