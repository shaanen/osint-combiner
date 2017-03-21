#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
import json


os.chdir(sys.path[0])

parser = argparse.ArgumentParser()
parser.add_argument("input", help="the input file or directory of files to be converted")
args = parser.parse_args()
if not Path(args.input).is_file():
    msg = "{0} is not an existing file".format(args.input)
    raise argparse.ArgumentTypeError(msg)

input_file = Path(args.input)
count = 0
with open('output.txt', 'w') as outfile:
    for str_banner in input_file.open(encoding='utf-8'):
        if '"bitcoin"' in str_banner:
            try:
                 banner = json.loads(str_banner)
                 try:
                    #print(banner['opts']['bitcoin']['handshake'][0]['nonce'])
                    banner['opts']['bitcoin']['handshake'][0]['nonce'] = str(banner['opts']['bitcoin']['handshake'][0]['nonce'])
                    count += 1
                    outfile.write(json.dumps(banner) + '\n')
                    #if count is 5:
                    #    sys.exit(0)
                 except (TypeError, KeyError):
                    pass
            except json.decoder.JSONDecodeError as e:
                print(e.args)
                print(str_banner)
print('Nr of times specific field found: ' + str(count)) 
