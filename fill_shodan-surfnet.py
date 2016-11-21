import shodan
import socket
import configparser
import sys
import json
from base import get_shodan_userinput

HOST = 'localhost'
PORT = 5040
config = configparser.ConfigParser()
config.read("keys.ini")
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
api = shodan.Shodan(SHODAN_API_KEY)
nrOfResults = 0
nrOfResultsSent = 0

chosen_query = get_shodan_userinput()
try:
    for banner in api.search_cursor(chosen_query):
        nrOfResults += 1
        msg = json.dumps(banner).encode('utf-8')
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print(msg)
            sys.exit(1)
        try:
            sock.connect((HOST, PORT))
        except socket.error as msg:
            print(msg)
            sys.exit(2)
        sock.send(msg)
        nrOfResultsSent += 1
except shodan.APIError as e:
        print('Error: ', e)
print("Results received:", nrOfResults)
print("Results sent: {}", nrOfResultsSent)
