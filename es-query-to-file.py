#!/usr/bin/env python3

from argparse import ArgumentParser
from netaddr import IPNetwork
from base import ask_output_file
import requests

r = requests.get('http://localhost:9200/mongodb-15feb/ip-address/_search?_source=_false&size=10000&q=(censys.location.country:Netherlands OR shodan.location.country:Netherlands)')

data = r.json()
path_output_file = ask_output_file('')
with open(path_output_file, 'w') as outfile:
    print('Total: ' + str(data['hits']['total']))
    for element in data['hits']['hits']:
        outfile.write(element['_id'] + '\n')
