import shodan
import configparser
import sys
import json

# For testing if Shodan API still works with given key

HOST = 'localhost'
PORT = 5040
config = configparser.ConfigParser()
config.read("keys.ini")
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
api = shodan.Shodan(SHODAN_API_KEY)

items = {'1': 'blablablabla', '2': 'asn:AS1101'}
choice = '0'
while choice not in items:
    choice = input("Choose query: (1='blablablabla' 2='asn:AS1101')")
chosenQuery = items[choice]

try:
    print("going in for loop")
    for banner in api.search_cursor(chosenQuery):
        msg = json.dumps(banner).encode('utf-8')
        print("banner: " + json.dumps(banner))
    print("end for loop")
except shodan.APIError as e:
        print('Error: ', e)
sys.exit(0)
