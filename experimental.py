import requests
import json
from censysobject import CensysObject

#just 1 result:
#path = 'https://storage.googleapis.com/censys-bigquery-export/12ad4f23-31ff-4854-b42a-0279ef9e2876-000000000000.json'
#multiple results:
path = 'https://storage.googleapis.com/censys-bigquery-export/698e332c-baac-412e-831a-5bc93ad62337-000000000000.json'

#TODO: PROBLEM TO SOLVE: json.loads fails when multiple results
response = requests.get(path)
str_path_output_file = 'outputfiles/censys/converted.json'
data = response.text.encode('utf-8')
censys_object = CensysObject()
print(type(data))
print(json.loads(str(data)))


