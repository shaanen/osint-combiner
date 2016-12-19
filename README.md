# vulnerabilityfinder
Combining OSINT sources in Elastic Stack

This project contains: 
+ various Python3 scripts for gathering data from OSINT sources; 
+ logstash config file

Project needs a file named "config.ini" with the following syntax:

[SectionOne]

ELASTICSEARCH_IP: *{IP of Elasticsearch cluster here}*

SHODANAPIKEY: *{Shodan API key here}*

CENSYS_API_ID: *{Censys API ID here}* 

CENSYS_API_KEY: *{Censys Secret here}* 

ZOOMEYE_USERNAME: *{Zoomeye e-mail here}*

ZOOMEYE_PASSWORD: *{Zoomeye password here}*

