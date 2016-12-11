#!/usr/bin/env python
# Reads CIDRs from file, uses ipinfo for each IP, saves output to outputfiles/ipinfo/ipinfo.json

from netaddr import IPNetwork
import threading
import requests
import logging

url = 'http://ipinfo.dutchsec.nl/submit'
headers = {'Content-Type': 'text/plain', 'Accept': 'text/json'}
path_output_file = 'outputfiles/ipinfo/ipinfo.json'
result_list = []
threads = []


# Threading class for one GET request
class GetIpInfoThread (threading.Thread):
    def __init__(self, target_ip):
        threading.Thread.__init__(self)
        self.target_ip = target_ip

    def run(self):
        print('Getting request for ip: %s' % self.target_ip + '...')
        try:
            resp = requests.post(url, headers=headers, data=str(self.target_ip))
        except requests.exceptions.ConnectionError:
            logging.warning("ConnectionError for ip %s" % self.target_ip)
            return
        result_list.append(resp.text)

# Start GetIpInfoThread per ip
for ip in IPNetwork('192.16.185.0/24'):
    thread = GetIpInfoThread(ip)
    thread.start()
    threads.append(thread)

# Wait for all GetIpInfoThreads to complete
for thread in threads:
    thread.join()

# Write all responses to file
nr_of_results = 0
with open(path_output_file, "a") as output_file:
    for item in result_list:
        nr_of_results += 1
        output_file.write(item)
        print('\r ' + str(nr_of_results) + " results written in" + path_output_file, end='')
