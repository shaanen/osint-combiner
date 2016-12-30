from base import is_valid_es_index_name
from base import exists_es_index
from base import es_get_distinct_ips
from base import es_get_distinct_ips_maybe_faster


str_input_es_index = ''
index_exists = False
while not index_exists:
    str_input_es_index = ''
    while not is_valid_es_index_name(str_input_es_index):
        str_input_es_index = input('Elasticsearch index name:')
    if exists_es_index(str_input_es_index):
        index_exists = True
    else:
        print('Index does not exist')
es_get_distinct_ips(str_input_es_index)
es_get_distinct_ips_maybe_faster(str_input_es_index)