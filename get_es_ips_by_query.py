from base import es_get_ips_by_query
from timetracker import TimeTracker
from base import check_outputfile
from base import exists_es_index
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('index', help='The Elasticsearch index.')
parser.add_argument("output", help="the output file which will contain the list of IPs")
args = parser.parse_args()
path_output_file = args.output
check_outputfile(path_output_file)
index = args.index
if not exists_es_index(index):
    msg = "{0} is not an existing Elasticsearch index".format(index)
    raise argparse.ArgumentTypeError(msg)

t = TimeTracker()
list_of_ips = es_get_ips_by_query(index)
with open(path_output_file, 'w') as outfile:
    for item in list_of_ips:
        outfile.write("%s\n" % item)
t.print_statistics()
