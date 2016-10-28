import censys.ipv4
import configparser
import json
import socket
import sys

HOST = 'localhost'
PORT = 5041
config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])

items = {'2': 'autonomous_system.asn: 1101', '3': 'custom query'}
choice = '0'
while choice not in items:
    choice = input("Choose query: (2='autonomous_system.asn: 1101' 3='custom query')")
chosenQuery = items[choice]
if chosenQuery is items['3']:
    chosenQuery = input("Enter Query: ")

censys = censys.ipv4.CensysIPv4(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
for record in censys.search(chosenQuery):
    msg = json.dumps(record).encode('utf-8')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(1)
    try:
        sock.connect((HOST, PORT))
        print("Sending data: " + json.dumps(record))
        sock.send(msg)
    except socket.error as msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(2)
