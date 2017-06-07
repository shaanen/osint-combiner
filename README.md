# OSINT Combiner
Combining OSINT sources in Elastic Stack

This project contains: 
+ various Python3 scripts which gather data from OSINT sources and convert them so they fit into Elasticsearch; 
+ logstash config files which use the outputfiles as input for Elasticsearch;
+ A wiki to build the project.

Currently supported OSINT sources:
+ [Shodan.io](https://www.shodan.io/ "Shodan's Homepage")
+ [Censys.io](https://censys.io/ "Censys' Homepage")
+ [IpInfo by DutchSec](http://dutchsec.nl/ "DutchSec's Homepage")

\- [Zoomeye](http://dutchsec.nl/ "Zoomeye's Homepage") is not yet supported because of limitations on their API. They don't respond on e-mails.

## Requirements

+ At least 1 VM to host the environment
+ Some open-source software components (will be discussed in the wiki)
+ A [Shodan.io](https://www.shodan.io/ "Shodan's Homepage") key for API access and scan credits
+ A [Censys.io](https://censys.io/ "Censys' Homepage") ID and KEY with [SQL and Export privileges](https://censys.io/contact "Censys' Contact page") 
  
## How to build
See the wiki [homepage](https://github.com/sjorsng/osint-combiner/wiki) for a visualization and steps to build the environment.
