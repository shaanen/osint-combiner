import shodan
import socket
import configparser
import sys
import json

HOST = 'localhost'
PORT = 5040
config = configparser.ConfigParser()
config.read("keys.ini")
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
api = shodan.Shodan(SHODAN_API_KEY)

items = {'1': 'blablablabla', '2': 'asn:AS1101', '3': 'custom query'}
choice = '0'
while choice not in items:
    choice = input("Choose query: (1='blablablabla' 2='asn:AS1101' 3='custom query')")
chosenQuery = items[choice]
if chosenQuery is items['3']:
    chosenQuery = input("Enter Query: ")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    sys.stderr.write("[ERROR] %s\n" % msg[1])
    sys.exit(1)

try:
    for banner in api.search_cursor(chosenQuery):
        msg = json.dumps(banner).encode('utf-8')
        try:
            sock.connect((HOST, PORT))
        except socket.error as msg:
            sys.stderr.write("[ERROR] %s\n" % msg[1])
            sys.exit(2)
        sock.send(msg)
except shodan.APIError as e:
        print('Error: ', e)
sock.close()
sys.exit(0)
