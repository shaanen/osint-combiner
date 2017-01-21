import configparser
import censys.export
import censys.query
from netaddr import IPNetwork
from base import dict_add_source_prefix
from base import dict_clean_empty
from base import ConcatJSONDecoder
import requests
import json
import re
import sys
import threading


class CensysObject:

    def __init__(self):
        """Return a CensysObject initialised with API ID and key"""
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
        self.CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
        self.api = censys.export.CensysExport(api_id=self.CENSYS_API_ID, api_secret=self.CENSYS_API_KEY)

    @staticmethod
    def get_latest_ipv4_tables(self):
        """Returns censys latest ipv4 snapshot string"""
        c = censys.query.CensysQuery(api_id=self.CENSYS_API_ID, api_secret=self.CENSYS_API_KEY)
        numbers = set()
        ipv4_tables = c.get_series_details("ipv4")['tables']
        for string in ipv4_tables:
            splitted_number = string.split('.')[1]
            if splitted_number != 'test':
                numbers.add(splitted_number)
        return max(numbers)

    @staticmethod
    def get_input_choice(self):
        """Returns input_choice represented as integer"""
        items = {'1': 'CIDR', '2': 'ASN', '3': 'CIDR file', '4': 'Custom WHERE query', '5': 'CSV file input'}
        input_choice = '0'
        while input_choice not in items:
            input_choice = input("Input: CIDR [1], ASN [2], CIDR file[3], custom query[4], or csv file input[5]?")
        return int(input_choice)

    @staticmethod
    def get_user_input_asn(self):
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

    @staticmethod
    def non_sql_get_user_input(self):
        """Returns Censys (non-SQL) query from user input"""
        items = {'2': 'autonomous_system.asn: 1101', '3': 'custom query'}
        choice = '0'
        while choice not in items:
            choice = input("Choose query: (2='autonomous_system.asn: 1101' 3='custom query')")
        chosen_query = items[choice]
        if chosen_query is items['3']:
            chosen_query = input("Enter Query: ")
        return chosen_query

    @staticmethod
    def sql_get_custom_query_from_user(self):
        """Returns Censys SQL query from user input (the part after 'WHERE')"""
        chosen_query = ''
        while chosen_query is '':
            chosen_query = input("select * from ipv4.[latest] where ")
        return chosen_query

    @staticmethod
    def prepare_ip_or_cidr_query(self, cidrs, latest_table=''):
        """Return Censys SQL query string for given CIDR or list of CIDRS"""
        if latest_table is '':
            latest_table = self.get_latest_ipv4_tables(self)
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

    @staticmethod
    def prepare_asn_query(self, asn):
        """Return Censys SQL query string for given CIDR"""
        latest_table = self.get_latest_ipv4_tables(self)
        print('Preparing Censys query for ASN ' + str(asn))
        return 'select * from ipv4.' + str(latest_table) + ' where autonomous_system.asn = ' + str(asn)

    @staticmethod
    def prepare_custom_query(self, query_part_after_where):
        """Return Censys SQL custom query string for given string"""
        latest_table = self.get_latest_ipv4_tables(self)
        return 'select * from ipv4.' + str(latest_table) + ' where ' + str(query_part_after_where)

    @staticmethod
    def to_file(self, query, str_path_output_file, should_convert):
        """Makes Censys Export request with given query, converts results and writes to output file
        :param self: CensysObject
        :param query: Strings which presents Censys SQL queries
        :param str_path_output_file: String which points to existing output file
        :param should_convert: Boolean if results should be converted
        """
        print("Executing query: " + query)

        config = configparser.ConfigParser()
        config.read("config.ini")
        CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
        CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
        api = censys.export.CensysExport(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)

        # Start new Job
        res = api.new_job(query, flatten=False)
        job_id = res["job_id"]
        result = api.check_job_loop(job_id)

        if result['status'] == 'success':
            total_results = 0
            for path in result['download_paths']:
                response = requests.get(path)
                list_of_json = json.loads(response.content.decode('utf-8'), cls=ConcatJSONDecoder)
                with open(str_path_output_file, 'a') as output_file:
                    for result in list_of_json:
                        result = dict_clean_empty(result)
                        if should_convert:
                            result = self.to_es_convert(self, result)
                        output_file.write(json.dumps(result) + '\n')
                total_results += len(list_of_json)
            print('Appended ' + str(total_results) + ' query results to ', str_path_output_file)
        else:
            print('Censys job failed.' + '\n' + str(result))

    @staticmethod
    def to_es_convert(self, input_dict):
        """Return dict ready to be sent to Logstash."""
        try:
            # convert ip_int to ipint
            input_dict['ip_int'] = input_dict['ipint']
            del input_dict['ipint']
        except KeyError:
            print(input_dict)
            print('Missing required IP field here. Exiting now...')
            sys.exit(1)
        try:
            # convert autonomous_system.asn to asn
            input_dict['asn'] = input_dict['autonomous_system']['asn']
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

        #  Remove 'p' from every protocol key
        pattern = re.compile("^p[0-9]{1,6}$")
        for key in input_dict:
            if pattern.match(key):
                input_dict[key[1:]] = input_dict[key]
                del input_dict[key]

        # prefix non-nested fields with 'censys'
        input_dict = dict_add_source_prefix(input_dict, 'censys')
        return input_dict


