#!/usr/bin/env python3
import censys.query
import configparser
import censysobject

config = configparser.ConfigParser()
config.read("config.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0

c = censys.export.CensysExport(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
censys_object = censysobject.CensysObject()
query = "select * from ipv4." + censys_object.get_latest_ipv4_tables(censys_object) + " where ip = \"8.8.8.8\""
print("Executing query: " + query)

# Start new Job
res = c.new_job(query)
job_id = res["job_id"]
result = c.check_job_loop(job_id)

if result['status'] == 'success':
    print(result)
    for path in result['download_paths']:
        print('all paths:')
        print(path)
else:
    print('Censys job failed.' + '\n' + str(result))