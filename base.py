from elasticsearch import Elasticsearch
import censys.query
import configparser
from netaddr import IPNetwork
from netaddr import IPSet
import re
import shodan
import json
import string

config = configparser.ConfigParser()
config.read("config.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
ES_IP = (config['SectionOne']['ELASTICSEARCH_IP'])
nrOfResults = 0


def es_get_distinct_ips(index):
    results = IPSet()
    es = Elasticsearch(([{'host': ES_IP}]))
    res_count = es.count(index=index)
    count = res_count['count']
    res = es.search(index=index,
                    body={"size": 0, "aggs": {"distinct_ip": {"terms": {"field": "ip", "size": count}}}})
    for hit in res['aggregations']['distinct_ip']['buckets']:
        results.add(hit)
    return results


def censys_get_latest_ipv4_tables():
    c = censys.query.CensysQuery(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
    numbers = []
    ipv4_tables = c.get_series_details("ipv4")['tables']
    for string in ipv4_tables:
        splitted_number = string.split('.')[1]
        if splitted_number != 'test':
            numbers.append(splitted_number)
    return max(numbers)


# Returns a non empty set of strings
def shodan_get_user_input_queries():
    queries = set()
    done = False
    while not done:
        items = {'1': 'blablablabla', '2': 'asn:AS1101', '3': 'custom query', '4': 'done'}
        choice = '0'
        while choice not in items:
            choice = input("Choose query: (1='blablablabla' 2='asn:AS1101' 3='custom query'). 4=done")
        chosen_query = items[choice]
        if chosen_query is items['3']:
            chosen_query = input("Enter Query: ")
        elif chosen_query is items['4']:
            if queries != set():
                done = True
        if chosen_query is not items['4']:
            queries.add(chosen_query)
    return queries


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


def parse_all_cidrs_from_file(file_path):
    l = []
    while not l:
        with open(file_path) as f:
            l = re.findall('(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?', f.read())
            print('CIDRs in file: ' + str(len(l)))
    return l


def to_file_shodan(queries, path_output_file):
    api = shodan.Shodan(SHODAN_API_KEY)
    nr_total_results = 0
    failed_queries = set()
    for query in queries:
        results = []
        try:
            for banner in api.search_cursor(query):
                results.append(json.dumps(banner) + '\n')
                print('\r' + str(len(results)) + ' results fetched...', end='')
        except shodan.APIError as e:
            print('Error: ', e)
            failed_queries.add(failed_queries)
        with open(path_output_file, "a") as output_file:
            for banner in results:
                output_file.write(banner)
        print('\r' + str(len(results)) + ' results written from query(' + query + ')')
        nr_total_results += len(results)
    # Print failed queries if present
    if not failed_queries == set():
        print('Failed queries: ', failed_queries)
    print(str(nr_total_results) + ' total results written in ' + path_output_file)


# valid file names may only contain: ascii_lowercase, digits, dot, dash, underscore
def is_valid_file_name(str_input):
    allowed = set(string.ascii_lowercase + string.digits + '.-_')
    if str_input is not '':
        return set(str_input) <= allowed
    return False

# def zoomeye_get_access_token(username, password):
