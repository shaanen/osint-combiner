from base import dict_add_source_prefix
from base import add_institution_field
from base import get_institutions
from base import dict_clean_empty
from base import convert_file
import configparser
import shodan
import json
import sys
import os


def get_new_shodan_api_object():
    """Returns initialised Shodan API object"""
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.realpath(__file__)) + "/config.ini")
    key = (config['osint_sources']['SHODAN_API_KEY'])
    return shodan.Shodan(key)


def shodan_to_es_convert(input_dict, institutions):
    """Returns dict ready to be used by the Elastic Stack."""
    try:
        # set ip and ip_int
        ip_int = input_dict['ip']
        del input_dict['ip']
        input_dict['ip'] = input_dict['ip_str']
        del input_dict['ip_str']
        input_dict['ip_int'] = ip_int
    except KeyError:
        try:
            input_dict['ip'] = input_dict['ip_str']
            del input_dict['ip_str']
        except KeyError:
            print(input_dict)
            print('Missing required \'ip\' field in the element above. Exiting now...')
            sys.exit(1)

    # if present, convert ssl.cert.serial to string
    try:
        input_dict['ssl']['cert']['serial'] = str(input_dict['ssl']['cert']['serial'])
    except KeyError:
        pass
    # if present, convert ssl.dhparams.generator to string
    try:
        input_dict['ssl']['dhparams']['generator'] = str(input_dict['ssl']['dhparams']['generator'])
    except (KeyError, TypeError):
        pass
    # if present, convert opts.bitcoin.handshake.nonce' to string
    # try:
    #     input_dict['opts']['bitcoin']['handshake'][0]['nonce'] = \
    #         str(input_dict['opts']['bitcoin']['handshake'][0]['nonce'])
    # except (KeyError, TypeError):
    #     pass

    try:
        # rename_shodan.modules to protocols (used as prefix per banner for combining multiple banners into 1 IP)
        input_dict['protocols'] = input_dict['_shodan']['module']
        # the rest of the data in _shodan is irrelevant
        del input_dict['_shodan']
    except KeyError:
        pass
    # asn to int
    try:
        input_dict['asn'] = int((input_dict['asn'])[2:])
    except KeyError:
        pass
    try:
        # rename location.country_name to location.country
        input_dict['location']['country'] = input_dict['location']['country_name']
        del input_dict['location']['country_name']
        # rename latitude and longitude for geoip
        input_dict['location']['geo'] = {}
        input_dict['location']['geo']['lat'] = input_dict['location']['latitude']
        input_dict['location']['geo']['lon'] = input_dict['location']['longitude']
        del input_dict['location']['latitude']
        del input_dict['location']['longitude']
    except KeyError:
        pass

    # Limit the number of fields
    input_dict = limit_nr_of_elements(input_dict)

    # prefix non-nested fields with 'shodan'
    input_dict = dict_add_source_prefix(input_dict, 'shodan', str(input_dict['protocols']))

    # If institutions are given, add institution field based on 'ip' field
    if institutions is not None:
        input_dict = add_institution_field(input_dict, institutions)

    return input_dict


def limit_nr_of_elements(input_dict):
    """Converts some of the JSON elements containing (too) many nested elements to 1 string element.
    This prevents Elasticsearch from making too many fields, so it is still manageable in Kibana.
    """
    try:
        input_dict['http']['components'] = str(
            input_dict['http']['components'])
    except KeyError:
        pass
    try:
        input_dict['elastic'] = str(
            input_dict['elastic'])
    except KeyError:
        pass
    try:
        input_dict['opts']['minecraft'] = str(
            input_dict['opts']['minecraft'])
    except KeyError:
        pass
    return input_dict


def to_file_shodan(queries, path_output_file, should_convert, should_add_institutions):
    """Makes a Shodan API call with each given query and writes results to output file
    :param queries: Collection of strings which present Shodan queries
    :param path_output_file: String which points to existing output file
    :param should_convert: Boolean if results should be converted
    :param should_add_institutions: boolean if an institution field should be added when converting
    """
    api = get_new_shodan_api_object()
    nr_total_results = 0
    failed_queries = set()
    for query in queries:
        print('\"' + query + '\"')
        results = 0
        with open(path_output_file, "a") as output_file:
            try:
                for banner in api.search_cursor(query):
                    banner = dict_clean_empty(banner)
                    output_file.write(json.dumps(banner) + '\n')
                    results += 1
                    print('\r' + str(results) + ' results written...', end='')
                print("")
            except shodan.APIError as e:
                print('Error: ', e)
                failed_queries.add(failed_queries)
        nr_total_results += results
    # Print failed queries if present
    if not failed_queries == set():
        print('Failed queries: ', failed_queries)

    print(str(nr_total_results) + ' total results written in ' + path_output_file)
    if should_convert:
        institutions = None
        if should_add_institutions:
            institutions = get_institutions()
        convert_file(path_output_file, 'shodan', institutions)


def get_input_choice():
    """Returns input_choice represented as integer"""
    items = ['1', '2', '3', '4']
    input_choice = '0'
    while input_choice not in items:
        input_choice = input("Console input[1], CIDR file input[2], csv file input[3] or query file input[4]?")
    return int(input_choice)


def get_user_input_console_queries():
    """Returns a non empty set of query strings"""
    queries = set()
    done = False
    print('Enter Shodan queries, one at a time. Enter \'4\' when done.')
    while not done:
            query = ''
            while query is '':
                query = input("Query:")
            if query is '4':
                if queries != set():
                    done = True
            else:
                queries.add(query)
    return queries
