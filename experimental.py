from elasticsearch import Elasticsearch
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
es_ip = (config['SectionOne']['ELASTICSEARCH_IP'])

es = Elasticsearch(([{'host': es_ip}]))
res = es.get(index="test", doc_type="ipinfo", id='AVj3xSKWYaPy3DV6oK90')['_source']
#res = es.count(index="test", body={"query": {"matchall": {}}})
print(res)
#res = es.search(index="test", body={"query": {"_exists_": {"ip"}}})