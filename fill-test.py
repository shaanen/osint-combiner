import base.ipv4
import configparser
import json
import socket
import sys
import shodan

HOST = 'localhost'
PORT = 5039
config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
query = "blablablabla"

base = base.ipv4.CensysIPv4(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
for record in censys.search(query):
    msg = json.dumps(record).encode('utf-8')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        sys.stderr.write("[ERROR] %s\n" % msg)
        sys.exit(1)
    try:
        sock.connect((HOST, PORT))
        print("Sending data: " + json.dumps(record))
        sock.send(msg)
    except socket.error as msg:
        sys.stderr.write("[ERROR] %s\n" % msg)
        sys.exit(2)

api = shodan.Shodan(SHODAN_API_KEY)
try:
    for banner in api.search_cursor(query):
        msg = json.dumps(banner).encode('utf-8')
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            sys.stderr.write("[ERROR] %s\n" % msg)
            sys.exit(1)
        try:
            sock.connect((HOST, PORT))
        except socket.error as msg:
            sys.stderr.write("[ERROR] %s\n" % msg)
            sys.exit(2)
        sock.send(msg)
        sock.close()
except shodan.APIError as e:
        print('Error: ', e)
