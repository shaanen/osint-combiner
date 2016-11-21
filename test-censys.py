import censys.ipv4
import configparser
import json
from base import censys_get_user_input

config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0

chosen_query = censys_get_user_input()

c = censys.ipv4.CensysIPv4(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
for record in c.search(chosen_query):
    nrOfResults += 1
    print(json.dumps(record))
print("Results received:", nrOfResults)
