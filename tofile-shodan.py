import shodan
import configparser
import json
from base import get_shodan_userinput

HOST = 'localhost'
PORT = 5040
config = configparser.ConfigParser()
config.read("keys.ini")
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
api = shodan.Shodan(SHODAN_API_KEY)
path_outputfile = 'outputfiles/shodan/shodan.json'
nrOfResults = 0

chosen_query = get_shodan_userinput()
try:
    with open(path_outputfile, "a") as outputfile:
        for banner in api.search_cursor(chosen_query):
            nrOfResults += 1
            outputfile.write(json.dumps(banner) + "\n")
            print('\r ' + str(nrOfResults) + " results written in" + path_outputfile, end='')
except shodan.APIError as e:
        print('Error: ', e)