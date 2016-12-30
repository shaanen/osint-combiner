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
from base import es_get_distinct_ips
from base import is_valid_es_index_name
from base import is_valid_file_name
from base import exists_es_index

url = 'http://ipinfo.dutchsec.nl/submit'
headers = {'Content-Type': 'text/plain', 'Accept': 'text/json'}
result_list = []
done_counter = 0
done_counter_lock = threading.Lock()
connection_err_counter = 0
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
        global connection_err_counter
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
                            connection_err_counter += 1
                    except requests.exceptions.ReadTimeout:
                        with timeout_err_lock:
                            timeout_err_counter += 1
                    finally:
                        print('\r' + str(done_counter) + ' done, ' + str(connection_err_counter) + ' connection errors, '
                              + str(timeout_err_counter) + ' timeouts', end='')
            else:
                queueLock.release()
            time.sleep(1)


def cidr_to_ipinfo(cidr_input, path_output_file):
    global exitFlag
    nr_threads = 0
    if len(cidr_input) < 16:
        nr_threads = len(cidr_input)
    else:
        nr_threads = 16
    if type(cidr_input) is IPNetwork:
        print('CIDR ' + str(cidr_input) + ' (' + str(cidr_input.size) + ' total)')
    elif type(cidr_input) is list:
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
    total_retries = connection_err_counter + timeout_err_counter
    if total_retries is not 0:
        print(str(total_retries) + ' times retried an IP')
    print(str(round((time.time() - start_time))) + ' seconds needed for getting all responses')

    # Write all responses to file
    with open(path_output_file, 'a') as output_file:
        # Writing newline if file is not empty
        if os.stat(path_output_file).st_size != 0:
            output_file.write('\n')

        output_file.write('\n'.join(result_list))
    print('\r' + str(len(result_list)) + ' results written in ' + path_output_file, end='')

ipinfo = IpInfoObject()
choice = ipinfo.get_input_choice(ipinfo)
cidrs = set()

str_name_output_file = ''
str_prefix_output_file = 'outputfiles/ipinfo/'
while not is_valid_file_name(str_name_output_file):
    str_name_output_file = input('Output file:' + str_prefix_output_file)
str_path_output_file = str_prefix_output_file + str_name_output_file

# 1= console input
if choice is 1:
    cidr_to_ipinfo(IPNetwork(get_cidr_from_user_input()), str_path_output_file)
# 2= CIDR file input
elif choice is 2:
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input file:')
    cidrs = parse_all_cidrs_from_file(input_file_path)
    print(cidrs, sep='\n')
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
    IPs = es_get_distinct_ips(str_input_es_index)
    cidr_to_ipinfo(IPs, str_path_output_file)
