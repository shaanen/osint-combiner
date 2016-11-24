import shodan
import configparser
import json
from base import shodan_get_user_input

config = configparser.ConfigParser()
config.read("keys.ini")
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
api = shodan.Shodan(SHODAN_API_KEY)
path_output_file = 'outputfiles/shodan/shodan.json'
nrOfResults = 0

chosen_query = shodan_get_user_input()
try:
    with open(path_output_file, "a") as outputfile:
        for banner in api.search_cursor(chosen_query):
            nrOfResults += 1
            outputfile.write(json.dumps(banner) + "\n")
            print('\r ' + str(nrOfResults) + " results written in" + path_output_file, end='')
except shodan.APIError as e:
        print('Error: ', e)
