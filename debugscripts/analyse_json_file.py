# --------------------------------------------------------------------------------------------
# Copyright (c) jehama en Sjors. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#!/usr/bin/env python3

"""Script for printing and counting presence of specific JSON fields from given file."""
# Imports
import argparse
import json
from pathlib import Path

# Gain arguments from the command line.
parser = argparse.ArgumentParser()
parser.add_argument("input", help="the input file")
parser.add_argument("fieldname", help="Field name (root level)")
parser.add_argument(
    "-s", "--silent", help="Don't print the found fields", action="store_true")
args = parser.parse_args()
if not Path(args.input).is_file():
    msg = "{0} is not an existing file".format(args.input)
    raise argparse.ArgumentTypeError(msg)

# The file to count the elements from.
input_file = Path(args.input)

# Counters to keep track of statistics.
total_count = 0
present_count = 0

# A loop used to count all json elements of the file.
for element in input_file.open():
    total_count += 1
    json_element = json.loads(element)
    try:
        # print JSON element(s), if present
        if not args.silent:
            print(str(json_element[args.fieldname]))
        present_count += 1
    except KeyError:
        pass

# print statistics
print("Given field: " + args.fieldname)
print("Given field present in: " + str(present_count) +
      "/" + str(total_count) + "total")
print("Given field missing: " + str(total_count - present_count))
