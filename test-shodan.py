import shodan
import configparser
import sys
import json

# For testing if Shodan API still works with given key

HOST = 'localhost'
PORT = 5040

config = configparser.ConfigParser()
config.read("keys.ini")

SHODAN_API_KEY = (config['SectionOne']['shodanapikey'])

api = shodan.Shodan(SHODAN_API_KEY)
try:
    print("going in for loop")
    for banner in api.search_cursor("apache"):
        msg = json.dumps(banner).encode('utf-8')
        print("banner: " + json.dumps(banner))
    print("end for loop")
except shodan.APIError as e:
        print('Error: ', e)
sys.exit(0)
