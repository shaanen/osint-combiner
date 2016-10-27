import sys
import censys
import configparser
from censys import *

config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])

api = censys.ipv4.CensysIPv4(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)

res = api.search("145.99.0.0/16")

matches = res['metadata']['count']
pageNum = matches / 100
if matches % 100 != 0:
    pageNum += 1

count = 1
while count <= pageNum:
    res = api.search("145.99.0.0/16", page=count)
    count += 1
    for i in res.get('results'):
        print("{} {}".format(i.get("ip"), " ".join(i.get('protocols'))))