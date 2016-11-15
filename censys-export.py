import censys.export
import configparser

config = configparser.ConfigParser()
config.read("keys.ini")
CENSYS_API_ID = (config['SectionOne']['CENSYS_API_ID'])
CENSYS_API_KEY = (config['SectionOne']['CENSYS_API_KEY'])
nrOfResults = 0

c = censys.export.CensysExport(api_id=CENSYS_API_ID, api_secret=CENSYS_API_KEY)

# Start new Job
res = c.new_job("select * from ipv4.20161112 where autonomous_system.asn = 1103 limit 1")
job_id = res["job_id"]

# Wait for job to finish and fetch results
print(c.check_job_loop(job_id))
