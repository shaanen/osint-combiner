import configparser
import censys.export
import censys.query
from netaddr import IPNetwork
from base import dict_add_source_prefix
from base import dict_clean_empty
from base import ConcatJSONDecoder
import requests
import json
import sys
import re
import os


def new_api_obj(str_type):
    """Returns initialised Censys SQL query API object"""
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.realpath(__file__)) + "/config.ini")
    censys_id = (config['SectionOne']['CENSYS_API_ID'])
    censys_key = (config['SectionOne']['CENSYS_API_KEY'])
    if str_type == 'SQL_QUERY':
        return censys.query.CensysQuery(api_id=censys_id, api_secret=censys_key)
    elif str_type == 'SQL_EXPORT':
        return censys.export.CensysExport(api_id=censys_id, api_secret=censys_key)


def get_latest_ipv4_tables():
    """Returns censys latest ipv4 snapshot string"""
    c = new_api_obj('SQL_QUERY')
    numbers = set()
    ipv4_tables = c.get_series_details("ipv4")['tables']
    for string in ipv4_tables:
        split_number = string.split('.')[1]
        if split_number != 'test':
            numbers.add(split_number)
    return max(numbers)


def get_input_choice():
    """Returns input_choice represented as integer"""
    items = ['1', '2', '3']
    input_choice = '0'
    while input_choice not in items:
        input_choice = input("Input: CIDR [1], ASN [2] or custom query[3]?")
    return int(input_choice)


def get_user_input_asn():
    """Asks user for ASN input and returns valid ASN number"""
    asn = -1
    valid_asn = False

    while not valid_asn:
        asn = input("Enter ASN:")
        if asn.isnumeric():
            asn = int(asn)
            if 0 <= asn <= 4294967295:
                valid_asn = True
    return asn


def non_sql_get_user_input():
    """Returns Censys (non-SQL) query from user input"""
    items = {'2': 'autonomous_system.asn: 1101', '3': 'custom query'}
    choice = '0'
    while choice not in items:
        choice = input("Choose query: (2='autonomous_system.asn: 1101' 3='custom query')")
    chosen_query = items[choice]
    if chosen_query is items['3']:
        chosen_query = input("Enter Query: ")
    return chosen_query


def sql_get_custom_query_from_user():
    """Returns Censys SQL query from user input (the part after 'WHERE')"""
    chosen_query = ''
    while chosen_query is '':
        chosen_query = input("select * from ipv4.[latest] where ")
    return chosen_query


def prepare_cidrs_query(cidrs, latest_table=''):
    """Returns Censys SQL query string for given CIDR or list of CIDRS"""
    if latest_table is '':
        latest_table = get_latest_ipv4_tables()
    query_builder = 'select * from ipv4.' + str(latest_table) + ' where '

    # Just one CIDR
    if type(cidrs) is IPNetwork:
        print('Preparing Censys query for ' + str(cidrs) + ', total: ' + str(cidrs.size))
        # 1 IP query
        if cidrs.size is 1:
            return query_builder + 'ip = "' + str(cidrs.network) + '"'
        # CIDR query
        else:
            start = cidrs.network
            end = cidrs.broadcast
            return query_builder + 'ipint BETWEEN ' + str(int(start)) + ' AND ' + str(int(end))
    # Multiple CIDRs
    else:
        first = True
        for cidr in cidrs:
            if first:
                first = False
            else:
                query_builder += ' OR '
            cidr = IPNetwork(cidr)
            start = cidr.network
            end = cidr.broadcast
            query_builder += 'ipint BETWEEN ' + str(int(start)) + ' AND ' + str(int(end))
        return query_builder


def prepare_asn_query(asn):
    """Returns Censys SQL query string for given CIDR"""
    latest_table = get_latest_ipv4_tables()
    print('Preparing Censys query for ASN ' + str(asn))
    return 'select * from ipv4.' + str(latest_table) + ' where autonomous_system.asn = ' + str(asn)


def prepare_custom_query(query_part_after_where, latest_table=''):
    """Returns Censys custom SQL query string for given string"""
    if latest_table is '':
        latest_table = get_latest_ipv4_tables()
    return 'select * from ipv4.' + str(latest_table) + ' where ' + str(query_part_after_where)


def to_file(query, str_path_output_file, should_convert):
    """Makes Censys Export request with given query, converts results and writes to output file
    :param query: Strings which presents Censys SQL queries
    :param str_path_output_file: String which points to existing output file
    :param should_convert: Boolean if results should be converted
    """
    c = new_api_obj('SQL_EXPORT')
    print("Executing query: " + query)
    # Start new Job
    res = c.new_job(query, flatten=False)
    job_id = res["job_id"]
    result = c.check_job_loop(job_id)

    if result['status'] == 'success':
        total_results = 0
        for path in result['download_paths']:
            response = requests.get(path)
            list_of_json = json.loads(response.content.decode('utf-8'), cls=ConcatJSONDecoder)
            with open(str_path_output_file, 'a') as output_file:
                for result in list_of_json:
                    result = dict_clean_empty(result)
                    if should_convert:
                        result = to_es_convert(result)
                    output_file.write(json.dumps(result) + '\n')
            total_results += len(list_of_json)
        if should_convert:
            print('Converted and appended ' + str(total_results) + ' query results to ', str_path_output_file)
        else:
            print('Appended ' + str(total_results) + ' query results to ', str_path_output_file)
    else:
        print('Censys job failed.' + '\n' + str(result))


def to_es_convert(input_dict):
    """Returns dict ready to be used by the Elastic Stack."""
    try:
        # convert ip_int to ipint
        input_dict['ip_int'] = input_dict['ipint']
        del input_dict['ipint']
    except KeyError:
        print(input_dict)
        print('Missing required IP field here. Exiting now...')
        sys.exit(1)
    try:
        # convert autonomous_system.asn to asn as integer
        input_dict['asn'] = int(input_dict['autonomous_system']['asn'])
        del input_dict['autonomous_system']['asn']
    except KeyError:
        pass
    try:
        # rename latitude and longitude for geoip
        input_dict['location']['geo'] = {}
        input_dict['location']['geo']['lat'] = input_dict['location']['latitude']
        input_dict['location']['geo']['lon'] = input_dict['location']['longitude']
        del input_dict['location']['latitude']
        del input_dict['location']['longitude']
    except KeyError:
        pass

    # Limit the number of fields
    input_dict = __limit_nr_of_elements(input_dict)

    #  Remove 'p' from every protocol key
    pattern = re.compile("^p[0-9]{1,6}$")
    for key in list(input_dict):
        if pattern.match(key):
            input_dict[key[1:]] = input_dict[key]
            del input_dict[key]

    # prefix non-nested fields with 'censys'
    input_dict = dict_add_source_prefix(input_dict, 'censys')
    return input_dict


def __limit_nr_of_elements(input_dict):
    """Converts some of the JSON elements containing (too) many nested elements to 1 string element.
    This prevents Elasticsearch from making too many fields, so it is still manageable in Kibana.
    """
    try:
        input_dict['p25']['smtp']['starttls']['tls']['chain'] = str(
            input_dict['p25']['smtp']['starttls']['tls']['chain'])
    except KeyError:
        pass
    try:
        input_dict['p110']['pop3']['starttls']['tls']['chain'] = str(
            input_dict['p110']['pop3']['starttls']['tls']['chain'])
    except KeyError:
        pass
    try:
        input_dict['p143']['imap']['starttls']['tls']['chain'] = str(
            input_dict['p143']['imap']['starttls']['tls']['chain'])
    except KeyError:
        pass
    try:
        input_dict['p443']['https']['tls']['chain'] = str(
            input_dict['p443']['https']['tls']['chain'])
    except KeyError:
        pass
    try:
        input_dict['p995']['pop3s']['tls']['tls']['chain'] = str(
            input_dict['p995']['pop3s']['tls']['tls']['chain'])
    except KeyError:
        pass
    return input_dict


