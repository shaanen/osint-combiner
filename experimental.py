import json


def change(input_json):
    input_json['location']['geo'] = {}
    input_json['location']['geo']['lat'] = input_json['location']['latitude']
    input_json['location']['geo']['lon'] = input_json['location']['longitude']
    del input_json['location']['latitude']
    del input_json['location']['longitude']
    return input_json


def recurse_keys(df, indent = '  '):
    '''
    import json, requests, pandas
    r = requests.post(...)
    rj = r.json() # json decode results query
    j = json.dumps(rj, sort_keys=True,indent=2)
    df1 = pandas.read_json(j)
    '''
    for key in df.keys():
        print(indent+str(key))
        if isinstance(df[key], dict):
            recurse_keys(df[key], indent+'   ')


def dict_add_source_prefix(obj, source_str, shodan_protocol_str=''):
    """Return dict where any non-nested element (except 'ip and ip_int') is prefixed by the OSINT source name"""
    keys_not_port_prefixed = ['asn', 'data', 'ip', 'ipv6 port', 'timestamp', 'hostnames', 'domains', 'location',
                              'location.area_code', 'location.city',  'location.country_code', 'location.country_code3',
                              'location.country_name', 'location.dma_code', 'location.latitude',  'location.longitude',
                              'location.postal_code', 'location.region_code', 'opts', 'org', 'isp', 'os', 'transport',
                              '[_shodan][module]']
    for key in obj.keys():
        print(key)
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


def shodan_to_es_convert(input_str):
    """Return str ready to be sent to Logstash."""
    input_json = json.loads(input_str)
    # set ip and ip_int
    ip_int = input_json['ip']
    del input_json['ip']
    input_json['ip'] = input_json['ip_str']
    input_json['ip_int'] = ip_int
    del input_json['ip_str']

    # convert ssl.cert.serial to string
    try:
        input_json['ssl']['cert']['serial'] = str(input_json['ssl']['cert']['serial'])
    except KeyError:
        pass
    # convert ssl.dhparams.generator to string
    try:
        input_json['ssl']['dhparams']['generator'] = str(input_json['ssl']['dhparams']['generator'])
    except (KeyError, TypeError):
        pass
    # rename _shodan to shodan
    # input_json['shodan'] = input_json['_shodan']
    # del input_json['_shodan']

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

    print('---')
    recurse_keys(input_json)
    print(' ')
    # prefix fields
    input_json = dict_add_source_prefix(input_json, 'shodan', str(input_json['_shodan']['module']))
    for key in input_json.keys():
        distinct_fields.add(key)
        total_fields_with_duplicates.append(key)

    return json.dumps(input_json)

distinct_fields = set()
total_fields_with_duplicates = []
banner_counter = 0
with open('outputfiles/shodan/shodan-changed-by-python.json', 'w') as a_file:
    for banner in open('outputfiles/shodan/shodan.json', 'r'):
        banner = shodan_to_es_convert(banner)
        a_file.write(banner)
        a_file.write('\n')
        banner_counter += 1
print(str(distinct_fields))
print('Nr of distinct fields: ' + str(len(distinct_fields)))
print('Total processed fields: ' + str(len(total_fields_with_duplicates)))
print('Total nr of documents: ' + str(banner_counter))

