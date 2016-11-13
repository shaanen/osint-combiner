import shodan
import configparser
import json

config = configparser.ConfigParser()
config.read("keys.ini")
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
api = shodan.Shodan(SHODAN_API_KEY)
nrOfResults = 0

items = {'1': 'blablablabla', '2': 'asn:AS1101', '3': 'custom query'}
choice = '0'
while choice not in items:
    choice = input("Choose query: (1='blablablabla' 2='asn:AS1101' 3='custom query')")
chosenQuery = items[choice]
if chosenQuery is items['3']:
    chosenQuery = input("Enter Query: ")

try:
    print("going through api.search_cursor...")
    for banner in api.search_cursor(chosenQuery):
        nrOfResults += 1
        print(json.dumps(banner))
    print("end api.search_cursor")
except shodan.APIError as e:
        print('Error: ', e)
print("Results received:", nrOfResults)
