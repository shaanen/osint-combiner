import shodan
import configparser
import json
from base import shodan_get_user_input_queries

config = configparser.ConfigParser()
config.read("keys.ini")
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
api = shodan.Shodan(SHODAN_API_KEY)
nrOfResults = 0

chosen_query = shodan_get_user_input_queries()

try:
    print("going through api.search_cursor...")
    for banner in api.search_cursor(chosen_query):
        nrOfResults += 1
        print(json.dumps(banner))
    print("end api.search_cursor")
except shodan.APIError as e:
        print('Error: ', e)
print("Results received:", nrOfResults)
