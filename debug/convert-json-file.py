#!/usr/bin/env python3
import json
from pathlib import Path

# DEBUG Script for converting specific JSON fields from given file and writing to output file

input_file = Path('../outputfiles/ipinfo/ipinfo-mongodb.json')
with open('../outputfiles/ipinfo/ipinfo-mongodb-converted.json', 'a') as output_file:
    for element in input_file.open():
        json_element = json.loads(element)
        try:
            json_element['ipinfo.whois']['person']['last_modified'] = \
                str(json_element['ipinfo.whois']['person']['last_modified'])
        except KeyError:
            pass
        output_file.write(json.dumps(json_element) + '\n')
