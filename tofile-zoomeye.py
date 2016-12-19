import configparser
import zoomeye

config = configparser.ConfigParser()
config.read("config.ini")
ZOOMEYE_USERNAME = (config['SectionOne']['ZOOMEYE_USERNAME'])
ZOOMEYE_PASSWORD = (config['SectionOne']['ZOOMEYE_PASSWORD'])
nrOfResults = 0
path_output_file = 'outputfiles/zoomeye/zoomeye.json'

zoomeye = zoomeye.ZoomEye(username=ZOOMEYE_USERNAME, password=ZOOMEYE_PASSWORD)
access_token = (zoomeye.login())
print(zoomeye.dork_search("country:cn"))



