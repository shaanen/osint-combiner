#!/usr/bin/env python
from netaddr import IPNetwork
from netaddr import core
from base import parse_all_cidrs_from_file
from base import exists_es_index
from base import es_get_all_ips
from pathlib import Path
import threading
import requests
import json
from datetime import datetime, timezone
import time
import os
import queue
import argparse
from ipinfofunctions import *
from base import dict_clean_empty

url = 'http://ipinfo.dutchsec.nl/submit'
headers = {'Content-Type': 'text/plain', 'Accept': 'text/json'}
result_list = []
done_counter = 0
done_counter_lock = threading.Lock()
conn_err_counter = 0
connection_err_lock = threading.Lock()
timeout_err_counter = 0
timeout_err_lock = threading.Lock()
exit_flag = 0
queueLock = threading.Lock()
workQueue = queue.Queue(0)
threads = []

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--convert", help="Convert immediately without storing original file.", action="store_true")
parser.add_argument("-y", "--yes", "--assume-yes", help="Automatic yes to prompts; assume \"yes\" as answer to all "
                                                        "prompts and run non-interactively.", action="store_true")
subparsers = parser.add_subparsers()
cidr = subparsers.add_parser('cidr', help='One CIDR input')
cidr.add_argument('inputcidr', help='The CIDR.')
cidr.add_argument('outputfile', help='The file where the results will be stored.')
cidr.set_defaults(subparser='cidr')

cidrfile = subparsers.add_parser('cidrfile', help='Textfile containing multiple CIDRs;')
cidrfile.add_argument("inputfile", help="the input file")
cidrfile.add_argument('outputfile', help='The file where the results will be stored.')
cidrfile.set_defaults(subparser='cidrfile')

elastic_index = subparsers.add_parser('elastic-index', help='Existing Elasticsearch index as input')
elastic_index.add_argument('index', help='The Elasticsearch index.')
elastic_index.add_argument('outputfile', help='The file where the results will be stored.')
elastic_index.set_defaults(subparser='elastic-index')

args = parser.parse_args()
choice = args.subparser
should_convert = args.convert
str_path_output_file = args.outputfile


# Threading class for one GET request
class GetIpInfoThread (threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q
        self.data = ''

    def run(self):
        global done_counter
        global conn_err_counter
        global timeout_err_counter
        while not exit_flag:
            queueLock.acquire()
            if not workQueue.empty():
                self.data = self.q.get()
                queueLock.release()
                got_valid_response = False
                while not got_valid_response:
                    try:
                        resp = requests.post(url, headers=headers, data=str(self.data), timeout=20)
                        resp_json = json.loads(resp.text)
                        resp_json['timestamp'] = str(datetime.now(timezone.utc).isoformat())
                        result_list.append(json.dumps(resp_json))
                        got_valid_response = True
                        with done_counter_lock:
                            done_counter += 1
                    except requests.exceptions.ConnectionError:
                        with connection_err_lock:
                            conn_err_counter += 1
                    except requests.exceptions.ReadTimeout:
                        with timeout_err_lock:
                            timeout_err_counter += 1
                    finally:
                        print('\r' + str(done_counter) + ' done, ' + str(conn_err_counter) + ' connection errors, '
                              + str(timeout_err_counter) + ' timeouts', end='')
            else:
                queueLock.release()
            time.sleep(1)


def cidr_to_ipinfo(cidr_input, path_output_file, should_be_converted):
    """Makes ipinfo request for every given IP or CIDR and writes to given file
    cidr_input -- A list of Strings or an IPNetwork
    """
    global exit_flag
    nr_threads = 0
    if type(cidr_input) is IPNetwork:
        if cidr_input.size < 16:
            nr_threads = cidr_input.size
        else:
            nr_threads = 16
        print('CIDR ' + str(cidr_input) + ' (' + str(cidr_input.size) + ' total)')
    else:
        if len(cidr_input) < 16:
            nr_threads = cidr_input.size
        else:
            nr_threads = 16
        print('List of IPs (' + str(len(cidr_input)) + ' total)')

    start_time = time.time()
    for num in range(1, nr_threads + 1):
        thread = GetIpInfoThread(workQueue)
        thread.start()
        threads.append(thread)

    # Fill the queue
    with queueLock:
        for ip in cidr_input:
            workQueue.put(ip)

    # Wait for queue to empty
    while not workQueue.empty():
        pass

    # Notify threads it's time to exit
    exit_flag = 1

    # Wait for all GetIpInfoThreads to complete
    for t in threads:
        t.join()
    print('')

    # Print useful statistics
    print(str((conn_err_counter + timeout_err_counter)) + ' times retried an IP')
    print(str(round((time.time() - start_time))) + ' seconds needed for getting all responses')

    # Write all responses to file
    with open(path_output_file, 'a') as output_file:

        # Writing newline if file is not empty
        if os.stat(path_output_file).st_size != 0:
            output_file.write('\n')
        # Remove empty elements, convert and write to output file
        for str_banner in result_list:
            banner = dict_clean_empty(json.loads(str_banner))
            if should_be_converted:
                banner = to_es_convert(banner)
            output_file.write(json.dumps(banner) + '\n')
    if should_convert:
        print(str(len(result_list)) + ' results converted and written in ' + path_output_file)
    else:
        print(str(len(result_list)) + ' results written in ' + path_output_file)

# 1= console CIDR input
if choice is 'cidr':
    try:
        cidr = IPNetwork(args.inputcidr)
    except core.AddrFormatError:
        msg = "{0} is not a valid IP or CIDR".format(args.inputfile)
        raise argparse.ArgumentTypeError(msg)
    cidr_to_ipinfo(cidr, str_path_output_file, should_convert)
# 2= CIDR file input
elif choice is 'cidrfile':
    if not Path(args.inputfile).is_file():
        msg = "{0} is not an existing file".format(args.inputfile)
        raise argparse.ArgumentTypeError(msg)
    cidrs = parse_all_cidrs_from_file(args.inputfile, should_convert)
    print(cidrs, sep='\n')
    all_cidrs_are_just_one_ip = True
    for cidr in cidrs:
        if IPNetwork(cidr).size is not 1:
            all_cidrs_are_just_one_ip = False
    # list of only single IPs
    if all_cidrs_are_just_one_ip:
        cidr_to_ipinfo(cidrs, str_path_output_file, should_convert)
    # list contains 1 or more CIDRS
    else:
        count = 0
        for cidr in cidrs:
            count += 1
            print('--Starting with CIDR: ' + cidr + ' (' + (str(count)) + '/' + str(len(cidrs)) + ')--')
            cidr_to_ipinfo(IPNetwork(cidr), str_path_output_file, should_convert)
            exit_flag = 0
# 3= Elasticsearch input
elif choice is 'elastic-index':
    if not exists_es_index(args.index):
        msg = "{0} is not an existing Elasticsearch index".format(args.inputfile)
        raise argparse.ArgumentTypeError(msg)
    list_of_ips = es_get_all_ips(args.index)
    cidr_to_ipinfo(list_of_ips, str_path_output_file, should_convert)
