import shodan
import configparser

config = configparser.ConfigParser()
config.read("keys.ini")

SHODAN_API_KEY = (config['SectionOne']['shodanapikey'])

api = shodan.Shodan(SHODAN_API_KEY)

# Wrap the request in a try/ except block to catch errors
try:
        # Search Shodan
        results = api.search('asn:AS1103')

        # Show the results
        print ('Results found: %s' % results['total'])
        for result in results['matches']:
                print ('IP: %s' % result['ip_str'])
                print (result['data'])
                print ('')
except shodan.APIError as e:
        print('Error: ', e)
