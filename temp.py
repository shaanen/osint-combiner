#!/usr/bin/env python
import re
input_dict = {'p25': 'blabla25', 'p80': 'blabla80', 'p110': 'blabla110', 'p995': 'blabla995'}
#  Remove 'p' from every protocol key
pattern = re.compile("^p[0-9]{1,6}$")
for key in input_dict:
    if pattern.match(key):
        input_dict[key[1:]] = input_dict[key]
        del input_dict[key]
print(str(input_dict))
