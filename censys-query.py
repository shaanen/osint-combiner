import censys.query
import configparser
from base import get_latest_ipv4

config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0

c = censys.query.CensysQuery(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)

# Start SQL job
res = c.new_job("select COUNT(*) from ipv4." + get_latest_ipv4())
job_id = res["job_id"]

# Wait for job to finish and get job metadata
print(c.check_job_loop(job_id))

# Iterate over the results from that job
print(c.get_results(job_id, page=1))
