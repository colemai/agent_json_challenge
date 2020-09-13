#!/usr/bin/env python3

"""
Author: Ian
Purpose: Code Test
Input:
Output:  
Sample Run: 
"""

import requests
import pdb
import json
import dateutil.parser
from datetime import timedelta
from datetime import datetime
import collections

dataset_api = "https://candidate.hubteam.com/candidateTest/v3/problem/dataset"
key = "780d080f13fe1d605c9e325d7afc" # should hash this or otherwise make it invisible
result_api = "https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=780d080f13fe1d605c9e325d7afc"


def get_req(payload = {}):
	base = dataset_api 
	try:
		response = requests.get(base, params=payload)
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


def post_req(payload = {}):
	base = result_api 
	response = requests.post(base, data=payload)
	return response


def split_partners_into_countries (full_data):
	""" Input: dict of api full response json
	Output: dict collating partners by country
	"""
	countries = {}
	for partner in full_data['partners']:
		country = partner['country']
		if country in countries.keys():
			countries[country].append(partner)
		else:
			countries[country] = [partner]
	return countries


def find_consensus_dates (country):
	""" Input: list of dicts - the output from split_partners_into_countries
	Output: dict, all required info for the given country
	"""
	
	# extract workable dates for each client
	for client in country:
		client['candidateDate'] = []
		dates = [dateutil.parser.parse(x) for x in client['availableDates']]
		dates = sorted(dates)
		for i in range(0, len(dates) - 1):
			if dates[i] + timedelta(days=1) == dates[i + 1]:
				client['candidateDate'].append(dates[i])
	
	# Find consensus dates for all clients of this country
	all_candidates = [[x for x in client['candidateDate']] for client in country]
	all_candidates = [item for sublist in all_candidates for item in sublist]
	all_candidates = sorted([my_date.strftime('%Y-%m-%d') for my_date in all_candidates])
	all_candidates = set(all_candidates)
	candidate_guestlist = {x:[] for x in all_candidates}
	for client in country:
		for date in all_candidates:
			client_slots = [my_date.strftime('%Y-%m-%d') for my_date in client['candidateDate']]
			if date in client_slots:
				candidate_guestlist[date].append(client['email'])
	slot_max = {x:len(y) for (x,y) in candidate_guestlist.items()}
	slot_max ={dateutil.parser.parse(x):y for (x,y) in slot_max.items()}
	slot_max = collections.OrderedDict(sorted(slot_max.items()))
	slot_max = {my_date.strftime('%Y-%m-%d'):y for (my_date,y) in slot_max.items()}
	best_date = max(slot_max, key=slot_max.get)
	attendees = candidate_guestlist[best_date]
	output =           {
			"attendeeCount": len(attendees),
			"attendees": attendees,
			"name": country[0]['country'],
			"startDate": best_date
		  }
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