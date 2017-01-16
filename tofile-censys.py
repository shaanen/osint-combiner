#!/usr/bin/env python3
from censysobject import CensysObject
from base import get_cidr_from_user_input
from base import ask_output_file
from base import ask_input_file
from base import parse_all_cidrs_from_file
from base import get_user_boolean
from base import get_organizations_from_csv
from base import ask_continue
from netaddr import IPNetwork
import threading
import time
import os.path
import queue

exitFlag = 0
nr_threads = 201
workQueue = queue.Queue(0)
threads = []
queueLock = threading.Lock()


# Threading class for one GET request
class CensysSQLExportThread (threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q
        self.query = ''
        self.path_output_file = ''
        self.should_convert = False

    def run(self):
        global exitFlag
        while not exitFlag:
            queueLock.acquire()
            if not workQueue.empty():
                self.query = self.q.get()[0]
                self.path_output_file = self.q.get()[1]
                self.should_convert = self.q.get()[2]
                queueLock.release()
                censys.to_file(censys, self.query, self.path_output_file, self.should_convert)
            else:
                queueLock.release()
            time.sleep(1)


def handle_organizations():
    for num in range(1, nr_threads + 1):
        thread = CensysSQLExportThread(workQueue)
        thread.start()
        threads.append(thread)

    # Fill the queue
    with queueLock:
        count = 0
        latest_table = censys.get_latest_ipv4_tables(censys)
        for name, cidrs in organizations.items():
            count += 1
            # print(name + ' [' + str(count) + '/' + str(len(organizations)) + ']...')
            organization_query = censys.prepare_ip_or_cidr_query(censys, cidrs, latest_table)
            if should_convert:
                path_output_file = 'outputfiles/censys/censys-' + name + '-converted.json'
            else:
                path_output_file = 'outputfiles/censys/censys-' + name + '.json'
            workQueue.put([organization_query, path_output_file, should_convert])

    # Wait for queue to empty
    while not workQueue.empty():
        pass

    # Notify threads it's time to exit
    global exitFlag
    exitFlag = 1

    # Wait for all GetIpInfoThreads to complete
    for t in threads:
        t.join()


censys = CensysObject()
choice = censys.get_input_choice(censys)
str_path_output_file = ''
if choice is not 5:
    str_path_output_file = ask_output_file('outputfiles/censys/')
should_convert = get_user_boolean('Also convert to es? y/n')

# 1=Console CIDR input
if choice is 1:
    cidr = get_cidr_from_user_input()
    query = censys.prepare_ip_or_cidr_query(censys, cidr)
    censys.to_file(censys, query, str_path_output_file, should_convert)
# 2=Console ASN input
elif choice is 2:
    asn = censys.get_user_input_asn(censys)
    query = censys.prepare_asn_query(censys, asn)
    censys.to_file(censys, query, str_path_output_file, should_convert)
# 3= CIDR file input
elif choice is 3:
    input_file = ask_input_file()
    set_cidrs = parse_all_cidrs_from_file(str(input_file))
    for cidr in set_cidrs:
        query = censys.prepare_ip_or_cidr_query(censys, IPNetwork(cidr))
        censys.to_file(censys, query, str_path_output_file, should_convert)
# 4=Console Custom WHERE query
elif choice is 4:
    query = censys.prepare_custom_query(censys, censys.sql_get_custom_query_from_user(censys))
    censys.to_file(censys, query, str_path_output_file, should_convert)
# 5= CSV file input
elif choice is 5:
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input CSV file:')
    organizations = get_organizations_from_csv(input_file_path)
    print(organizations.keys())
    print(str(len(organizations)) + ' organizations found.')
    ask_continue()
    handle_organizations()


