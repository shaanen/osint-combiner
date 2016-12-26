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
        results.add(hit["key"])
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


# valid file names may only contain: ascii_lowercase, digits, dot, dash, underscore
def is_valid_file_name(str_input):
    allowed = set(string.ascii_lowercase + string.digits + '.-_')
    if str_input is not '':
        return set(str_input) <= allowed
    return False


def dict_add_source_prefix(obj, source_str, shodan_protocol_str=''):
    """Return dict where any non-nested element (except 'ip and ip_int') is prefixed by the OSINT source name"""
    keys_not_port_prefixed = ['asn', 'data', 'ip', 'ipv6 port', 'hostnames', 'domains', 'location',
                              'location.area_code', 'location.city',  'location.country_code', 'location.country_code3',
                              'location.country_name', 'location.dma_code', 'location.latitude',  'location.longitude',
                              'location.postal_code', 'location.region_code', 'opts', 'org', 'isp', 'os', 'transport',
                              'protocols']
    for key in obj.keys():
        # prefix all non-nested elements except ip and ip_int
        if '.' not in key and key is not 'ip' and key is not 'ip_int':
            # if anything else then shodan, just prefix source
            if shodan_protocol_str is '':
                new_key = key.replace(key, (source_str + "." + key))
            # if shodan
            else:
                # just prefix source if general shodan key
                if key in keys_not_port_prefixed:
                    new_key = key.replace(key, (source_str + "." + key))
                # prefix source AND shodan.module (protocol) if protocol-specific key
                else:
                    new_key = key.replace(key, (source_str + "." + shodan_protocol_str + '.' + key))
            if new_key != key:
                obj[new_key] = obj[key]
                del obj[key]
    return obj


def print_json_tree(df, indent='  '):
    for key in df.keys():
        print(indent+str(key))
        if isinstance(df[key], dict):
            print_json_tree(df[key], indent + '   ')

# def zoomeye_get_access_token(username, password):
