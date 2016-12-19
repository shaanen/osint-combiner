import censys.export
import configparser
import urllib.request
import shutil
from base import censys_get_user_input_asn
from base import censys_get_latest_ipv4_tables

config = configparser.ConfigParser()
config.read("config.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0
path_output_file = 'outputfiles/censys/censys.json'

asn = censys_get_user_input_asn()

c = censys.export.CensysExport(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)
latest_table = censys_get_latest_ipv4_tables()
query = "select * from ipv4." + str(latest_table) + " where autonomous_system.asn = " + str(asn)
print("Executing query: " + query)
# Start new Job
res = c.new_job(query)
job_id = res["job_id"]

result = c.check_job_loop(job_id)

if result['status'] == 'success':
    print(result)
    for path in result['download_paths']:
        with urllib.request.urlopen(path) as response, open(path_output_file, 'ab') as out_file:
            shutil.copyfileobj(response, out_file)
            print('Got file from URL: ' + response.geturl())
            print("Appended results to", path_output_file)
else:
    print('Censys job failed.' + '\n' + str(result))
