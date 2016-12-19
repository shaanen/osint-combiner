from elasticsearch import Elasticsearch
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
es_ip = (config['SectionOne']['ELASTICSEARCH_IP'])

es = Elasticsearch(([{'host': es_ip}]))
res_count = es.count(index="as1103-new2")
count = res_count['count']
res = es.search(index="as1103-new2", body={"size":0,"aggs":{"distinct_ip":{"terms":{"field":"ip", "size": count}}}})
for hit in res['aggregations']['distinct_ip']['buckets']:
	print(hit["key"])
