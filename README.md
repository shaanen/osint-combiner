# OSINT Combiner
Combining OSINT sources in Elastic Stack

This project contains: 
+ various Python3 scripts which gather data from OSINT sources, convert them so they fit into Elasticsearch and write the results to outputfiles/*; 
+ logstash config files which use the outputfiles as input for Elasticsearch.

Currently supported OSINT sources:
+ [Shodan.io](https://www.shodan.io/ "Shodan's Homepage")
+ [Censys.io](https://censys.io/ "Censys' Homepage")
+ [IpInfo by DutchSec](http://dutchsec.nl/ "DutchSec's Homepage")

\- [Zoomeye](http://dutchsec.nl/ "Zoomeye's Homepage") is not yet supported because of limitations on their API. They don't respond on e-mails.

## Requirements

+ A [Shodan.io](https://www.shodan.io/ "Shodan's Homepage") key for API access and scan credits
+ A [Censys.io](https://censys.io/ "Censys' Homepage") ID and KEY with [SQL and Export privileges](https://censys.io/contact "Censys' Contact page") 
+ Project needs a text file named "config.ini" with the following content:

```
[osint_sources]

SHODAN_API_KEY: *{Shodan API key here}*

CENSYS_API_ID: *{Censys API ID here}* 

CENSYS_API_KEY: *{Censys Secret here}*

[elastic]

ELASTICSEARCH_IP: *{IP of Elasticsearch cluster here}*

X-PACK_ENABLED: *{Whether X-PACK is enabled (true/false}*

X-PACK_USERNAME: *{(optional) X-PACK SHIELD username here}*

X-PACK_PASSWORD: *{(optional) X-PACK SHIELD password here}*

```

+ The Python3 scripts need the following modules (can be installed with easy_install3 or pip3): 
  + Shodan
  + Censys
  + Elasticsearch
  + Netaddr
  
## How to use
You can run the following scripts:
 + tofile-\*.py files take arguments and can be runned automatically, for example with a CRON job. Run with the '-h' flag for more info;
 + tofile-\*-manually.py files will ask for user input interactively;
 + convert-\*.py files can convert the resulting files from tofile-\*.py to Elasticsearch compatible files, if not already converted with the '-c' flag from tofile-\*.py;
 + Scripts in debugscripts/ can be used for debugging purposes.

The \*.conf files are Logstash configuration files which you need to edit so the config will point to the right files and Elasticsearch index.

Elasticsearch needs a specific mapping to import the data from the scripts. Use the mapping in the [Wiki](https://github.com/sjorsng/vulnerabilityfinder/wiki#required-elasticsearch-mapping-for-indexes "The Github Wiki of this project"). 
