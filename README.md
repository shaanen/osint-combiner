# vulnerabilityfinder
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
[SectionOne]

ELASTICSEARCH_IP: *{IP of Elasticsearch cluster here}*

SHODANAPIKEY: *{Shodan API key here}*

CENSYS_API_ID: *{Censys API ID here}* 

CENSYS_API_KEY: *{Censys Secret here}*
```

+ The Python3 scripts need the following modules (can be installed with easy_install3 or pip3): 
  + Shodan
  + Censys
  + Elasticsearch
  + Netaddr
  
## How to use
When running a tofile-\*.py script, it will ask a for choice in user input:
 + Various query options directly via the console input;
 + CIDR file input: which parses all CIDRs from a given text file;
 + CSV file input: which parses names of organizations (column 1) with the corresponding CIDR (column 2). Can take multiple CIDRs per organization, where each CIDR is on a separate row. Will create an outputfile per organization;
 + Elasticsearch index input (for IpInfo): Takes all the distinct IP adresses from given Elasticsearch index. Fastest and best option for IpInfo, because it will only query IpInfo for IPs used by real network devices. Shodan and/or Censys did already do the device discovery, so let IpInfo only query the IPs which are found by those sources. Quering IpInfo with large CIDRs will take ages, and probably most IPs in such CIDR is not used by a device anyway.

The scripts will ask if the results should be converted to the Elasticsearch format immediately. If you choose not to, you can convert the resulting files at a later time with the convert-\*-file.py scripts. Regardless of this choice, the scripts will always remove empty fields from the results, so the outputfiles will be much smaller in size.

The \*.conf files are Logstash configuration files which you need to edit so the config will point to the right files and Elasticsearch index. 
In the near future I may create a Github wiki which will contain instructions on how to create the right Elasticsearch mapping for the output files.  
