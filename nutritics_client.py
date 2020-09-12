#!/usr/bin/env python3

"""
Author: Ian
Purpose: Call Nutritics API
Input:
Output:  
Sample Run: 


HTTP
200s success
300s redirects
400s client errors like no permission to view that
500s server errors like server down

http://httpbin.org/
"""

from sys import argv
import json
import jmespath
import requests
import re
import pdb

api_base = "https://httpbin.org/"

# payload = {'page': 2, 'count': 25}
# r = requests.get('https://httpbin.org/get', params=payload)


def get_req(payload = {}):
	base = api_base + "get"
	response = requests.get(base, params=payload)
	return response


if __name__ == "__main__":
	response = get_req({'page': 2, 'count': 25})
	print(response.text)