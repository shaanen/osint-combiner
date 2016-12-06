 #Reads CIDRs from file, uses ipinfo for each IP, saves output to outputfiles/ipinfo/ipinfo.json
 #curl -X POST --data "8.8.8.8" http://ipinfo.dutchsec.nl/submit -H "Content-Type: text/plain" -H "Accept: text/json"
import requests

url = 'http://ipinfo.dutchsec.nl/submit'
headers = {'Content-Type: text/plain', 'Accept: text/json'}
data = '8.8.8.8'

resp = requests.post(url, headers=headers, data=data)
if resp and resp.status_code == 200:
    print(resp.json)