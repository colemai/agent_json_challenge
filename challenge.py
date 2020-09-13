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


>>> r = requests.put('https://httpbin.org/put', data = {'key':'value'})
>>> r = requests.delete('https://httpbin.org/delete')
>>> r = requests.head('https://httpbin.org/get')
>>> r = requests.options('https://httpbin.org/get')


PASS IN HEADERS
>>> url = 'https://api.github.com/some/endpoint'
>>> headers = {'user-agent': 'my-app/0.0.1'}

>>> r = requests.get(url, headers=headers)

"""

import requests
import pdb
import json
import dateutil.parser
from datetime import timedelta
from datetime import datetime
import collections

dataset_base = "https://candidate.hubteam.com/candidateTest/v3/problem/dataset"
key = "780d080f13fe1d605c9e325d7afc"
result_base = "https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=780d080f13fe1d605c9e325d7afc"

def get_req(payload = {}):
	base = dataset_base 
	response = requests.get(base, params=payload)
	return response

def post_req(payload = {}):
	base = result_base 
	response = requests.post(base, data=payload)
	return response

def split_partners_into_countries (full_data):
	countries = {}
	for partner in full_data['partners']:
		country = partner['country']
		if country in countries.keys():
			countries[country].append(partner)
		else:
			countries[country] = [partner]
	return countries

def find_consensus_dates (country):
	# pdb.set_trace()
	for client in country:
		client['slot'] = []
		dates = [dateutil.parser.parse(x) for x in client['availableDates']]
		dates = sorted(dates)
		for i in range(0, len(dates) - 1):
			if dates[i] + timedelta(days=1) == dates[i + 1]:
				client['slot'].append(dates[i])
	# Now we have available slots per client
	all_slots = [[x for x in client['slot']] for client in country]
	all_slots = [item for sublist in all_slots for item in sublist]
	all_slots = sorted([my_date.strftime('%Y-%m-%d') for my_date in all_slots])
	all_slots = set(all_slots)
	slot_count = {x:[] for x in all_slots}
	for client in country:
		for slot in all_slots:
			client_slots = [my_date.strftime('%Y-%m-%d') for my_date in client['slot']]
			if slot in client_slots:
				slot_count[slot].append(client['email'])
	slot_max = {x:len(y) for (x,y) in slot_count.items()}
	slot_max ={dateutil.parser.parse(x):y for (x,y) in slot_max.items()}
	slot_max = collections.OrderedDict(sorted(slot_max.items()))
	slot_max = {my_date.strftime('%Y-%m-%d'):y for (my_date,y) in slot_max.items()}
	best_date = max(slot_max, key=slot_max.get)
	attendees = slot_count[best_date]
	output =           {
            "attendeeCount": len(attendees),
            "attendees": attendees,
            "name": country[0]['country'],
            "startDate": best_date
          }
	# pdb.set_trace()
	return output



if __name__ == "__main__":
	params = {"userKey" : key}
	response = get_req(params)

	countries = split_partners_into_countries(response.json())
	result = []
	for country in countries.values():
		result.append(find_consensus_dates(country))
	result = json.dumps({"countries":result})
	# response = post_req(result)

	# print(countries)
	# print(response.json())
	pdb.set_trace()
	# print(response.text)