#!/usr/bin/env python3
import censys.ipv4
import configparser
import json
import socket
import sys
from censysobject import CensysObject
HOST = 'localhost'
PORT = 5041
config = configparser.ConfigParser()
config.read("config.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0
nrOfResultsSent = 0

censys_object = CensysObject()
chosen_query = censys_object.non_sql_get_user_input(censys_object)

c = censys.ipv4.CensysIPv4(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
for record in c.search(chosen_query):
    nrOfResults += 1
    msg = json.dumps(record).encode('utf-8')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(1)
    try:
        sock.connect((HOST, PORT))
        sock.send(msg)
        nrOfResultsSent += 1
    except socket.error as msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(2)
print("Results received:", nrOfResults)
print("Results sent: {}", nrOfResultsSent)
