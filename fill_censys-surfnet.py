import censys.ipv4
import configparser
import json
import socket
import sys

HOST = 'localhost'
PORT = 5040
config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])

censys = censys.ipv4.CensysIPv4(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
for record in censys.search("autonomous_system.asn: 1101"):
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
