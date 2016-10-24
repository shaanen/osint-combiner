import shodan
import configparser
import simplejson
import requests

config = configparser.ConfigParser()
config.read("keys.ini")

SHODAN_API_KEY = (config['SectionOne']['shodanapikey'])

api = shodan.Shodan(SHODAN_API_KEY)

try:
    for banner in api.search_cursor("asn:AS1101"):#asn:AS1101
        with open("shodan.txt", "a") as myfile:
            myfile.write(simplejson.dumps(banner))

        #r = requests.post('http://145.100.181.87:9200/shodan-surfnet/', data=bannerinjson)
        #print(r)
except shodan.APIError as e:
        print('Error: ', e)
