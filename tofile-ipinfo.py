#!/usr/bin/env python
from netaddr import IPNetwork
import threading
import requests
import json
from datetime import datetime, timezone
import time
import os
import queue
from ipinfoobject import IpInfoObject
from base import get_cidr_from_user_input
from base import parse_all_cidrs_from_file
from base import es_get_all_ips
from base import is_valid_es_index_name
from base import exists_es_index
from base import ask_output_file
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
exitFlag = 0
queueLock = threading.Lock()
workQueue = queue.Queue(0)
threads = []


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
        while not exitFlag:
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


def cidr_to_ipinfo(cidr_input, path_output_file):
    """Makes ipinfo request for every given IP or CIDR and writes to given file

    cidr_input -- A list of Strings or an IPNetwork
    """
    global exitFlag
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
    exitFlag = 1

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
            ipinfo.to_es_convert(ipinfo, banner)
            output_file.write(json.dumps(banner) + '\n')
    print('\r' + str(len(result_list)) + ' results written in ' + path_output_file, end='')

ipinfo = IpInfoObject()
choice = ipinfo.get_input_choice(ipinfo)
str_path_output_file = ask_output_file('outputfiles/ipinfo/')

# 1= console CIDR input
if choice is 1:
    cidr_to_ipinfo(get_cidr_from_user_input(), str_path_output_file)
# 2= CIDR file input
elif choice is 2:
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input file:')
    cidrs = parse_all_cidrs_from_file(input_file_path)
    print(cidrs, sep='\n')
    all_cidrs_are_just_one_ip = True
    for cidr in cidrs:
        if IPNetwork(cidr).size is not 1:
            all_cidrs_are_just_one_ip = False
    # list of only single IPs
    if all_cidrs_are_just_one_ip:
        cidr_to_ipinfo(cidrs, str_path_output_file)
    # list contains 1 or more CIDRS
    else:
        for cidr in cidrs:
            print('--Starting with CIDR: ' + cidr + ' (' + (str(cidrs.index(cidr) + 1)) + '/' + str(len(cidrs)) + ')--')
            cidr_to_ipinfo(IPNetwork(cidr), str_path_output_file)
# 3= Elasticsearch Input
elif choice is 3:
    str_input_es_index = ''
    index_exists = False
    while not index_exists:
        str_input_es_index = ''
        while not is_valid_es_index_name(str_input_es_index):
            str_input_es_index = input('Elasticsearch index name:')
        if exists_es_index(str_input_es_index):
            index_exists = True
        else:
            print('Index does not exist')
    list_of_ips = es_get_all_ips(str_input_es_index)
    cidr_to_ipinfo(list_of_ips, str_path_output_file)
