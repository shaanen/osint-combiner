#!/usr/bin/env python
# Reads CIDRs from user input, uses ipinfo for each IP, saves output to outputfiles/ipinfo/ipinfo.json

import threading
import requests
import json
from datetime import datetime
import time
import base
import os

url = 'http://ipinfo.dutchsec.nl/submit'
headers = {'Content-Type': 'text/plain', 'Accept': 'text/json'}
path_output_file = 'outputfiles/ipinfo/ipinfo.json'
result_list = []
threads = []
done_counter = 0
done_counter_lock = threading.Lock()
failed_counter = 0
failed_counter_lock = threading.Lock()
IPs = base.get_cidr_from_user_input()


# Threading class for one GET request
class GetIpInfoThread (threading.Thread):
    def __init__(self, target_ip):
        threading.Thread.__init__(self)
        self.target_ip = target_ip

    def run(self):
        global done_counter
        global failed_counter
        got_valid_response = False
        while not got_valid_response:
            print('\r' + str(done_counter) + ' done, ' + str(failed_counter) + ' failed', end='')
            try:
                resp = requests.post(url, headers=headers, data=str(self.target_ip))
                resp_json = json.loads(resp.text)
                resp_json['timestamp'] = str(datetime.now())
                result_list.append(json.dumps(resp_json))
                got_valid_response = True
                with done_counter_lock:
                    done_counter += 1
            # except requests.exceptions.ConnectionError:
            except:
                with failed_counter_lock:
                    failed_counter += 1
        print('\r' + str(done_counter) + ' done, ' + str(failed_counter) + ' failed', end='')

print('---Getting info for CIDR ' + str(IPs) + ' (' + str(IPs.size) + ' total)---')
start_time = time.time()

# Start GetIpInfoThread per ip
for ip in IPs:
    thread = GetIpInfoThread(ip)
    thread.start()
    threads.append(thread)

# Wait for all GetIpInfoThreads to complete
for thread in threads:
    thread.join()
print('')

# Print useful statistics
print(str(failed_counter) + ' times retried an IP')
print(str(round((time.time() - start_time))) + ' seconds needed for getting all responses')

# Write all responses to file
with open(path_output_file, 'a') as output_file:
    # Writing newline if file is not empty
    if os.stat(path_output_file).st_size != 0:
        output_file.write('\n')

    output_file.write('\n'.join(result_list))
print('\r' + str(len(result_list)) + ' results written in ' + path_output_file, end='')
