import shodan
import configparser
import json
from base import dict_add_source_prefix


class ShodanObject:

    def __init__(self):
        """Return a ShodanObject initialised with API key"""
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.SHODAN_API_KEY = (config['SectionOne']['SHODAN_API_KEY'])
        self.api = api = shodan.Shodan(self.SHODAN_API_KEY)

    @staticmethod
    def shodan_to_es_convert(self, input_str):
        """Return str ready to be sent to Logstash."""
        input_json = json.loads(input_str)

        # set ip and ip_int
        ip_int = input_json['ip']
        del input_json['ip']
        input_json['ip'] = input_json['ip_str']
        input_json['ip_int'] = ip_int
        del input_json['ip_str']

        # if present, convert ssl.cert.serial to string
        try:
            input_json['ssl']['cert']['serial'] = str(input_json['ssl']['cert']['serial'])
        except KeyError:
            pass
        # if present, convert ssl.dhparams.generator to string
        try:
            input_json['ssl']['dhparams']['generator'] = str(input_json['ssl']['dhparams']['generator'])
        except (KeyError, TypeError):
            pass
        # rename_shodan.modules to protocols (used as prefix per Shodan banner for combining multiple banners into 1 IP)
        input_json['protocols'] = input_json['_shodan']['module']
        # the rest of the data in _shodan is irrelevant
        del input_json['_shodan']

        # asn value to lowercase
        input_json['asn'] = str.lower(input_json['asn'])
        # rename location.country_name to location.country
        input_json['location']['country'] = input_json['location']['country_name']
        del input_json['location']['country_name']
        # rename latitude and longitude for geoip
        input_json['location']['geo'] = {}
        input_json['location']['geo']['lat'] = input_json['location']['latitude']
        input_json['location']['geo']['lon'] = input_json['location']['longitude']
        del input_json['location']['latitude']
        del input_json['location']['longitude']

        # prefix non-nested fields with 'shodan'
        input_json = dict_add_source_prefix(input_json, 'shodan', str(input_json['protocols']))
        return json.dumps(input_json)

    @staticmethod
    def to_file_shodan(self, queries, path_output_file):
        """Makes a Shodan API call with each given query and writes results to output file
        :param self: ShodanObject
        :param queries: Collection of strings which present Shodan queries
        :param path_output_file: String which points to existing output file
        """
        nr_total_results = 0
        failed_queries = set()
        for query in queries:
            results = []
            try:
                for banner in self.api.search_cursor(query):
                    banner = self.shodan_to_es_convert(self, json.dumps(banner))
                    results.append(banner + '\n')
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

    @staticmethod
    def get_input_choice(self):
        """Returns input_choice represented as integer"""
        items = {'1': 'console_input', '2': 'cidr_file_input'}
        input_choice = '0'
        while input_choice not in items:
            input_choice = input("Console input[1] or CIDR file input[2]?")
        return int(input_choice)

    # Returns a non empty set of query strings
    @staticmethod
    def get_user_input_queries():
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

