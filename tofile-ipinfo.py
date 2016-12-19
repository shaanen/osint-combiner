#!/usr/bin/env python
# Reads CIDRs from user input, uses ipinfo for each IP, saves output to outputfiles/ipinfo/ipinfo.json
from netaddr import IPSet
import threading
import requests
import json
from datetime import datetime
import time
import os
import queue
from base import get_cidr_from_user_input
from base import parse_all_cidrs_from_file
from base import es_get_distinct_ips

url = 'https://ipinfo.dutchsec.nl/submit'
headers = {'Content-Type': 'text/plain', 'Accept': 'text/json'}
path_output_file = 'outputfiles/ipinfo/ipinfo.json'
result_list = []
done_counter = 0
done_counter_lock = threading.Lock()
connection_err_counter = 0
connection_err_lock = threading.Lock()
timeout_err_counter = 0
timeout_err_lock = threading.Lock()
exitFlag = 0
queueLock = threading.Lock()
# nr_threads = 32
workQueue = queue.Queue(0)
threads = []
# IPs = base.get_cidr_from_user_input()
#IPs = IPNetwork('194.53.92.0/24')


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
                        resp_json['timestamp'] = str(datetime.now())
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


def cidr_to_ipinfo(IPs):
    global exitFlag
    nr_threads = 0
    if IPs.size < 16:
        nr_threads = IPs.size
    else:
        nr_threads = 16
    print('CIDR ' + str(IPs) + ' (' + str(IPs.size) + ' total)')
    start_time = time.time()

    for num in range(1, nr_threads + 1):
        thread = GetIpInfoThread(workQueue)
        thread.start()
        threads.append(thread)

    # Fill the queue
    with queueLock:
        for ip in IPs:
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
    print(str((connection_err_counter + timeout_err_counter)) + ' times retried an IP')
    print(str(round((time.time() - start_time))) + ' seconds needed for getting all responses')

    # Write all responses to file
    with open(path_output_file, 'a') as output_file:
        # Writing newline if file is not empty
        if os.stat(path_output_file).st_size != 0:
            output_file.write('\n')

        output_file.write('\n'.join(result_list))
    print('\r' + str(len(result_list)) + ' results written in ' + path_output_file, end='')


def get_choice():
    items = {'1': 'console_input', '2': 'cidr_file_input', '3': 'elasticsearch_input'}
    nr = '0'
    while nr not in items:
        nr = input("Console input[1], CIDR file input[2] or Elasticsearch input[3]?")
    return nr

choice = get_choice()
cidrs = set()
if choice is '1':
    cidr_to_ipinfo(IPNetwork(get_cidr_from_user_input()))
elif choice is '2':
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input file:')
    cidrs = parse_all_cidrs_from_file(input_file_path)
    print(cidrs, sep='\n')
    for cidr in cidrs:
        print('--Starting with CIDR: ' + cidr + ' (' + (str(cidrs.index(cidr) + 1 )) + '/' + str(len(cidrs)) + ')--')

        cidr_to_ipinfo(IPSet(cidr))
elif choice is '3':
    IPs = es_get_distinct_ips('as1103-new')
    cidr_to_ipinfo(IPs)
