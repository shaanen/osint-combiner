#!/usr/bin/env python3
from censysfunctions import *
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

exit_flag = 0
nr_threads = 4
work_queue = queue.Queue(0)
threads = []
queue_lock = threading.Lock()


# Threading class for one GET request
class CensysSQLExportThread (threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q
        self.query = ''
        self.path_output_file = ''
        self.should_convert = False

    def run(self):
        global exit_flag
        while not exit_flag:
            queue_lock.acquire()
            if not work_queue.empty():
                self.query = self.q.get()[0]
                self.path_output_file = self.q.get()[1]
                self.should_convert = self.q.get()[2]
                queue_lock.release()
                # to_file(self.query, self.path_output_file, self.should_convert)
                print('Thread run: ' + self.path_output_file)
                time.sleep(1)
            else:
                queue_lock.release()
            time.sleep(1)


def to_file_organizations():
    for num in range(1, nr_threads + 1):
        thread = CensysSQLExportThread(work_queue)
        thread.start()
        threads.append(thread)

    # Fill the queue
    with queue_lock:
        latest_table = get_latest_ipv4_tables()
        print('len organizations.items: ' + str(len(organizations.items())))
        for name, cidrs in organizations.items():
            organization_query = prepare_cidrs_query(cidrs, latest_table)
            path_output_file = 'outputfiles/censys/censys-' + name
            if should_convert:
                path_output_file += '-converted.json'
            else:
                path_output_file += '.json'
            work_queue.put([organization_query, path_output_file, should_convert])
            print(work_queue)

    # Wait for queue to empty
    while not work_queue.empty():
        pass

    # Notify threads it's time to exit
    global exit_flag
    exit_flag = 1

    # Wait for all GetIpInfoThreads to complete
    for t in threads:
        t.join()

choice = get_input_choice()
str_path_output_file = ''
if choice is not 5:
    str_path_output_file = ask_output_file('outputfiles/censys/')
should_convert = get_user_boolean('Also convert to es? y/n')

# 1=Console CIDR input
if choice is 1:
    cidr = get_cidr_from_user_input()
    query = prepare_cidrs_query(cidr)
    to_file(query, str_path_output_file, should_convert)
# 2=Console ASN input
elif choice is 2:
    asn = get_user_input_asn()
    query = prepare_asn_query(asn)
    to_file(query, str_path_output_file, should_convert)
# 3= CIDR file input
elif choice is 3:
    input_file = ask_input_file()
    set_cidrs = parse_all_cidrs_from_file(str(input_file))
    query = prepare_cidrs_query(set_cidrs)
    to_file(query, str_path_output_file, should_convert)
# 4=Console Custom WHERE query
elif choice is 4:
    query = prepare_custom_query(sql_get_custom_query_from_user())
    to_file(query, str_path_output_file, should_convert)
# 5= CSV file input
elif choice is 5:
    input_file_path = ''
    while not os.path.isfile(input_file_path):
        input_file_path = input('Input CSV file:')
    organizations = get_organizations_from_csv(input_file_path)
    print(organizations.keys())
    print(str(len(organizations)) + ' organizations found.')
    ask_continue()
    to_file_organizations()
