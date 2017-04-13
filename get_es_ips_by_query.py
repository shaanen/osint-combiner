from base import es_get_ips_by_query
from timetracker import TimeTracker
from base import check_outputfile
from base import exists_es_index
from base import ask_continue
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('index', help='The ES index.')
parser.add_argument('query', help='The ES query. The query should be enclosed with double quotes. Using '
                                  'double quotes withing the ES query itself should be escaped with a backslash')
parser.add_argument("output", help="the output file which will contain the list of IPs")
parser.add_argument("-y", "--yes", "--assume-yes", help="Automatic yes to prompts; assume \"yes\" as answer to all "
                                                        "prompts and run non-interactively.", action="store_true")
args = parser.parse_args()
path_output_file = args.output
check_outputfile(path_output_file)
index = args.index
query = args.query
if not exists_es_index(index):
    msg = "{0} is not an existing Elasticsearch index".format(index)
    raise argparse.ArgumentTypeError(msg)

t = TimeTracker()
list_of_ips = es_get_ips_by_query(index, query)
if not args.yes:
    ask_continue()
with open(path_output_file, 'w') as outfile:
    for item in list_of_ips:
        outfile.write("%s\n" % item)
t.print_statistics()
