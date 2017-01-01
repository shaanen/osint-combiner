from base import dict_add_source_prefix


class IpInfoObject:

    @staticmethod
    def to_es_convert(self, input_dict):
        """Return dict ready to be sent to Logstash."""

        # rename location elements
        input_dict['location'] = {}
        try:
            input_dict['location']['country'] = input_dict['geo']['country']['name']
        except KeyError:
            pass
        try:
            input_dict['location']['country_code'] = input_dict['geo']['country']['iso_code']
        except KeyError:
            pass
        del input_dict['geo']['country']
        try:
            input_dict['location']['city'] = input_dict['geo']['city']
        except KeyError:
            pass

        # rename latitude and longitude for geoip
        try:
            input_dict['location']['geo'] = {}
            input_dict['location']['geo']['lat'] = input_dict['geo']['location']['latitude']
            input_dict['location']['geo']['lon'] = input_dict['geo']['location']['longitude']
        except KeyError:
            pass
        del input_dict['geo']['location']
        try:
            if not input_dict['geo']:
                del input_dict['geo']
        except KeyError:
            pass

        # prefix non-nested fields with 'ipinfo'
        input_dict = dict_add_source_prefix(input_dict, 'ipinfo')
        return input_dict

    @staticmethod
    def get_input_choice(self):
        """Returns input_choice represented as integer"""
        items = {'1': 'console_input', '2': 'cidr_file_input', '3': 'elasticsearch_input'}
        input_choice = '0'
        while input_choice not in items:
            input_choice = input("Console input[1], CIDR file input[2] or Elasticsearch input[3]?")
        return int(input_choice)



