#!/usr/bin/env python3

"""
Author: Ian
Purpose: Call Nutritics API
Input:
Output:  
Sample Run: 


HTTP
100s informational
200s success
300s redirects
400s client errors like no permission to view that
500s server errors like server down

http://httpbin.org/

response.text
.url
.content  -> raw bytes
.text  -> string version
.headers -> gives dict I think
.status
.json()


Auth metods:

requests.get('https://api.github.com/user', auth=HTTPBasicAuth('username', 'password'))

my_headers = {'Authorization' : 'Bearer {access_token}'}
response = requests.get('http://httpbin.org/headers', headers=my_headers)

session = requests.Session()
session.headers.update({'Authorization': 'Bearer {access_token}'})
response = session.get('https://httpbin.org/headers')


JSON:
from dict
json.dumps(dict, sort_keys=True, indent=4)

to file
with open('user.json','w') as file:
         json.dump(dict, file, sort_keys=True, indent=4)



POST a file:
files = {'upload_file': open('file.txt','rb')}
values = {'DB': 'photcat', 'OUT': 'csv', 'SHORT': 'short'}

r = requests.post(url, files=files, data=values)


"""

from sys import argv
import json
import jmespath
import requests
import re
import pdb
import json

api_base = "https://@www.nutritics.com/api/v1.1/"
username = "iancoleman1a"
password = ""

def get_req(payload = {}):
	base = api_base + "get"
	response = requests.get(base, params=payload)
	return response

def get_req_with_auth(username, password, payload = {}):
	base = api_base + "get"
	response = requests.get(base, params=payload, auth=(username, password))
	return response

def post_req(payload = {}):
	""" Create a new resource """
	base = api_base + "post"
	response = requests.post(base, data=payload)
	return response

def put_req(payload = {}):
	""" Update a resource """
	base = api_base + "put"
	response = requests.put(base, data=payload)
	return response

def request_foundation (req_type, payload = {}):
	""" INPUT: request type string, payload dict
		Robustly perform GET request on API 
		Checking for http and response-type errors"""
	base = api_base + req_type
	try:
		if req_type == "LIST/":
	    	response = requests.get(base, params=payload, auth=(username, password))
	   	elif "CREATE" in req_type:
	   		## NOT WORKING at least for nutritics -> internal server error
	   		response = requests.post(base, data=payload, auth=(username, password))
	    response.raise_for_status()
	except requests.exceptions.HTTPError as errh:
	    print(errh)
	except requests.exceptions.ConnectionError as errc:
	    print(errc)
	except requests.exceptions.Timeout as errt:
	    print(errt)
	except requests.exceptions.RequestException as err:
	    print(err)
	assert 'json' in response.headers['Content-Type'], "Response isn't json!"

	return response

def get_nutritics_objects (payload = {}):
	response = request_foundation('LIST/', payload)
	return response

def post_nutritics_object (object_type, payload = {}):
	response = request_foundation('CREATE/' + object_type, payload)
	return response 


if __name__ == "__main__":
	response = get_nutritics_objects({'client': ''})
	print(response.json())
	# pdb.set_trace()
	# print(response.text)

	john = {"dob": "2000-10-16", "gender": "m", "height": 1.70, "weight": 70}