import shodan
import configparser
import json

HOST = 'localhost'
PORT = 5040
config = configparser.ConfigParser()
config.read("keys.ini")
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
api = shodan.Shodan(SHODAN_API_KEY)
path_outputfile = 'outputfiles/shodan/shodan.json'
nrOfResults = 0

items = {'1': 'blablablabla', '2': 'asn:AS1101', '3': 'custom query'}
choice = '0'
while choice not in items:
    choice = input("Choose query: (1='blablablabla' 2='asn:AS1101' 3='custom query')")
chosenQuery = items[choice]
if chosenQuery is items['3']:
    chosenQuery = input("Enter Query: ")
try:
    with open(path_outputfile, "a") as outputfile:
        for banner in api.search_cursor(chosenQuery):
            nrOfResults += 1
            outputfile.write(json.dumps(banner) + "\n")
except shodan.APIError as e:
        print('Error: ', e)
print(nrOfResults, "results written in", path_outputfile)
