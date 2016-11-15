import censys.query
import configparser

config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0

c = censys.query.CensysQuery(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)

# find datasets (e.g., ipv4) that have exposed data
print(c.get_series())

# get schema and tables for a given dataset
print(c.get_series_details("ipv4"))

# Start SQL job
res = c.new_job("select count(*) from certificates.certificates")
job_id = res["job_id"]

# Wait for job to finish and get job metadata
print(c.check_job_loop(job_id))

# Iterate over the results from that job
print(c.get_results(job_id, page=1))
