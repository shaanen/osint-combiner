#!/usr/bin/env python3
from timetracker import TimeTracker
from base import check_outputfile
from base import exists_es_index
from base import es_get_all
import argparse
import sys
import os

os.chdir(sys.path[0])

parser = argparse.ArgumentParser()
parser.add_argument('index', help='The Elasticsearch index.')
parser.add_argument("output", help="the output file which will contain the retrieved Elasticsearch documents")
args = parser.parse_args()
path_output_file = args.output
check_outputfile(path_output_file)
index = args.index
if not exists_es_index(index):
    msg = "{0} is not an existing Elasticsearch index".format(index)
    raise argparse.ArgumentTypeError(msg)

t = TimeTracker()
documents = es_get_all(index)
with open(path_output_file, 'w') as outfile:
    for item in documents:
        outfile.write("%s\n" % item)
t.print_statistics()
