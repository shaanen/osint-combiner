import configparser
import censys.export
from base import dict_add_source_prefix
import re


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
    def get_user_input(self):
        """Returns (non-SQL) Censys query from user input"""
        items = {'2': 'autonomous_system.asn: 1101', '3': 'custom query'}
        choice = '0'
        while choice not in items:
            choice = input("Choose query: (2='autonomous_system.asn: 1101' 3='custom query')")
        chosen_query = items[choice]
        if chosen_query is items['3']:
            chosen_query = input("Enter Query: ")
        return chosen_query

    @staticmethod
    def to_es_convert(self, input_dict):
        """Return dict ready to be sent to Logstash."""
        # convert ip_int to ipint
        input_dict['ip_int'] = input_dict['ipint']
        del input_dict['ipint']
        # convert autonomous_system.asn to asn
        input_dict['asn'] = input_dict['autonomous_system']['asn']
        del input_dict['autonomous_system']['asn']

        # rename latitude and longitude for geoip
        input_dict['location']['geo'] = {}
        input_dict['location']['geo']['lat'] = input_dict['location']['latitude']
        input_dict['location']['geo']['lon'] = input_dict['location']['longitude']
        del input_dict['location']['latitude']
        del input_dict['location']['longitude']

        #  Remove 'p' from every protocol key
        pattern = re.compile("^p[0-9]{1,6}$")
        for key in input_dict:
            if pattern.match(key):
                input_dict[key[1:]] = input_dict[key]
                del input_dict[key]

        # prefix non-nested fields with 'censys'
        input_dict = dict_add_source_prefix(input_dict, 'censys')
        return input_dict
