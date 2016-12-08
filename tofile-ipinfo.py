 #Reads CIDRs from file, uses ipinfo for each IP, saves output to outputfiles/ipinfo/ipinfo.json
 #curl -X POST --data "8.8.8.8" http://ipinfo.dutchsec.nl/submit -H "Content-Type: text/plain" -H "Accept: text/json"
import requests
from netaddr import IPNetwork

url = 'http://ipinfo.dutchsec.nl/submit'
headers = {'Content-Type': 'text/plain', 'Accept': 'text/json'}
path_output_file = 'outputfiles/ipinfo/ipinfo.json'
list = []

for ip in IPNetwork('192.16.185.0/31'):
    print('Get request for ip: %s' % ip)
    resp = requests.post(url, headers=headers, data=str(ip))
    print('Response: ' + resp.text)
    list.append(resp.text)

with open(path_output_file, "a") as outputfile:
    for item in list:
        outputfile.write(item)
