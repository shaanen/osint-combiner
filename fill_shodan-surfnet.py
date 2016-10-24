import shodan
import socket
import configparser
import sys
import json

HOST = 'localhost'
PORT = 5040

config = configparser.ConfigParser()
config.read("keys.ini")

SHODAN_API_KEY = (config['SectionOne']['shodanapikey'])

api = shodan.Shodan(SHODAN_API_KEY)

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    sys.stderr.write("[ERROR] %s\n" % msg[1])
    sys.exit(1)

try:
    sock.connect((HOST, PORT))
except socket.error as msg:
    sys.stderr.write("[ERROR] %s\n" % msg[1])
    sys.exit(2)

try:
    for banner in api.search_cursor("asn:AS1101"):
        msg = json.dumps(banner).encode('utf-8')
        sock.send(msg)
except shodan.APIError as e:
        print('Error: ', e)


sock.close()
sys.exit(0)
