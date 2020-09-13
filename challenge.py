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


def extract_candidate_dates (country):
	""" Input: list of dicts - the output from split_partners_into_countries
	Output: list of dicts, like input but with ['candidateDates']
	"""
	for client in country:
		client['candidateDates'] = []
		dates = [dateutil.parser.parse(x) for x in client['availableDates']]
		dates = sorted(dates)
		for i in range(0, len(dates) - 1):
			if dates[i] + timedelta(days=1) == dates[i + 1]:
				client['candidateDates'].append(dates[i])
	return country


def find_consensus_dates (country):
	""" Input: list of dicts - the output from extract_candidate_dates 
	Output: dict, all required output info for this country 
	"""
	# Make a sorted list of all possible dates in string format
	candidates = [[x for x in client['candidateDates']] for client in country]
	candidates = [item for sublist in candidates for item in sublist]
	candidates = set(candidates)
	candidates = sorted(candidates) # note this turns set into list
	candidates = [my_date.strftime('%Y-%m-%d') for my_date in candidates]
	# candidates = set(candidates)
	candidate_guestlist = {x:[] for x in candidates}
	for client in country:
		for date in candidates:
			client_slots = [my_date.strftime('%Y-%m-%d') for my_date in client['candidateDates']]
			if date in client_slots:
				candidate_guestlist[date].append(client['email'])
	slot_max = {x:len(y) for (x,y) in candidate_guestlist.items()}
	# slot_max ={dateutil.parser.parse(x):y for (x,y) in slot_max.items()}
	# slot_max = collections.OrderedDict(sorted(slot_max.items()))
	# slot_max = {my_date.strftime('%Y-%m-%d'):y for (my_date,y) in slot_max.items()}
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
		country_with_client_dates = extract_candidate_dates(country)
		result.append(find_consensus_dates(country_with_client_dates))
	result = json.dumps({"countries":result})
	print(result)
	response = post_req(result)
	print(response)
	# print(countries)
	# print(response.json())
	# pdb.set_trace()
	# print(response.text)