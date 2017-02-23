from base import dict_add_source_prefix


def to_es_convert(input_dict):
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
    return input_dict




