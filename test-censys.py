import base_censys.ipv4
import configparser
import json
import socket
import sys

config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0

items = {'2': 'autonomous_system.asn: 1101', '3': 'custom query'}
choice = '0'
while choice not in items:
    choice = input("Choose query: (2='autonomous_system.asn: 1101' 3='custom query')")
chosenQuery = items[choice]
if chosenQuery is items['3']:
    chosenQuery = input("Enter Query: ")

base_censys = base_censys.ipv4.CensysIPv4(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
for record in censys.search(chosenQuery):
    nrOfResults += 1
    print(json.dumps(record))
print("Results received:", nrOfResults)
