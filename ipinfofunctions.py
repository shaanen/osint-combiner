from base import dict_add_source_prefix
from base import add_institution_field


def ipinfo_to_es_convert(input_dict, institutions):
    """Returns dict ready to be used by the Elastic Stack."""

    # rename location elements
    input_dict['location'] = {}
    try:
        input_dict['location']['country'] = input_dict['geo']['country']['name']
    except KeyError:
        pass
    try:
        input_dict['location']['country_code'] = input_dict['geo']['country']['iso_code']
        del input_dict['geo']['country']
    except KeyError:
        pass
    try:
        input_dict['location']['city'] = input_dict['geo']['city']
    except KeyError:
        pass

    # rename latitude and longitude for geoip
    try:
        input_dict['location']['geo'] = {}
        input_dict['location']['geo']['lat'] = input_dict['geo']['location']['latitude']
        input_dict['location']['geo']['lon'] = input_dict['geo']['location']['longitude']
        del input_dict['geo']['location']
    except KeyError:
        pass
    try:
        if not input_dict['geo']:
            del input_dict['geo']
    except KeyError:
        pass

    # prefix non-nested fields with 'ipinfo'
    input_dict = dict_add_source_prefix(input_dict, 'ipinfo')

    # If institutions are given, add institution field based on 'ip' field
    if institutions is not None:
        input_dict = add_institution_field(input_dict, institutions)

    return input_dict
