# Reads CIDRs from file, uses ipinfo for each IP, saves output to outputfiles/ipinfo/ipinfo.json

from netaddr import IPNetwork
import threading
import requests
import logging
import json
from datetime import datetime

url = 'http://ipinfo.dutchsec.nl/submit'
headers = {'Content-Type': 'text/plain', 'Accept': 'text/json'}
path_output_file = 'outputfiles/ipinfo/ipinfo.json'
cidr = '192.104.140.0/27'
result_list = []
threads = []


# Threading class for one GET request
class GetIpInfoThread (threading.Thread):
    def __init__(self, target_ip):
        threading.Thread.__init__(self)
        self.target_ip = target_ip

    def run(self):
        # print('Getting ip: %s' % self.target_ip + '...')
        got_valid_response = False
        while not got_valid_response:
            try:
                resp = requests.post(url, headers=headers, data=str(self.target_ip))
                resp_json = json.loads(resp.text)
                resp_json['timestamp'] = str(datetime.now())
                result_list.append(json.dumps(resp_json))
                got_valid_response = True
            except requests.exceptions.ConnectionError:
                logging.warning("ConnectionError for ip %s" % self.target_ip + " retrying now...")
            # print('Done ip: %s' % self.target_ip)



IPs = IPNetwork(cidr)
print('---Getting info for CIDR ' + cidr + ' (' + str(IPs.size) + ' total)---')
# Start GetIpInfoThread per ip
for ip in IPs:
    thread = GetIpInfoThread(ip)
    thread.start()
    threads.append(thread)

# Wait for all GetIpInfoThreads to complete
for thread in threads:
    thread.join()
print(str(IPs.size) + ' IPs in CIDR ' + cidr)

# Write all responses to file
with open(path_output_file, "a") as output_file:
    output_file.write('\n'.join(result_list))

print('\r' + str(len(result_list)) + " results written in" + path_output_file, end='')

