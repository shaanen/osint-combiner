import censys.query
import configparser
from netaddr import IPNetwork

config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0


def censys_get_latest_ipv4_tables():
    c = censys.query.CensysQuery(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
    numbers = []
    ipv4_tables = c.get_series_details("ipv4")['tables']
    for string in ipv4_tables:
        splitted_number = string.split('.')[1]
        if splitted_number != 'test':
            numbers.append(splitted_number)
    return max(numbers)


def shodan_get_user_input():
    items = {'1': 'blablablabla', '2': 'asn:AS1101', '3': 'custom query'}
    choice = '0'
    while choice not in items:
        choice = input("Choose query: (1='blablablabla' 2='asn:AS1101' 3='custom query')")
    chosen_query = items[choice]
    if chosen_query is items['3']:
        chosen_query = input("Enter Query: ")
    return chosen_query


def censys_get_user_input_asn():
    asn = -1
    valid_asn = False

    while not valid_asn:
        asn = input("Enter ASN:")
        if asn.isnumeric():
            asn = int(asn)
            if 0 <= asn <= 4294967295:
                valid_asn = True
    return asn


def censys_get_user_input():
    items = {'2': 'autonomous_system.asn: 1101', '3': 'custom query'}
    choice = '0'
    while choice not in items:
        choice = input("Choose query: (2='autonomous_system.asn: 1101' 3='custom query')")
    chosen_query = items[choice]
    if chosen_query is items['3']:
        chosen_query = input("Enter Query: ")
    return chosen_query


def get_cidr_from_user_input():
    ip_or_cidr = '0'
    while not isinstance(ip_or_cidr, IPNetwork):
        try:
            ip_or_cidr = IPNetwork(input("IP/CIDR: "))
        except:
            print('Not a valid IP/CIDR.')
    return ip_or_cidr

#def zoomeye_get_access_token(username, password):
