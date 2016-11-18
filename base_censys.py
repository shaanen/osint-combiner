import censys.query
import configparser

config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0


def get_latest_ipv4():
    c = censys.query.CensysQuery(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
    numbers = []
    ipv4_tables = c.get_series_details("ipv4")['tables']
    for string in ipv4_tables:
        splitted_number = string.split('.')[1]
        if splitted_number != 'test':
            numbers.append(splitted_number)
    return max(numbers)

