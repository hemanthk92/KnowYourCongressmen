from pymongo import MongoClient
import json
from os.path import isfile, join
from os import listdir
import pandas as pd
import json 
import numpy
import sys


def get_votes_data(congress):
	'''
	Input: congress (str) string to specify congress #
	Retrieves bill information and voting records from files. Filters the columns and rows
	Output: data['bills'] list of dictionaries of bill info and voting records
	'''
	df = pd.read_csv('../data/%s_bills_ids.csv' %congress)
	with open('../data/%s_votes.json' %congress) as dataf:
		data = json.load(dataf)

	for i in xrange(len(data['bills'])):
		bill_id = data['bills'][i].keys()[0]
		temp = df[df['id'] == int(bill_id)]

		for column in temp.columns:
			data['bills'][i][column] = temp.iloc[0][column]
			data['bills'][i]['vote_voter'] = data['bills'][i][bill_id]
			#looping through each column in the bills_id dataframe and appending to data['bills'] dictionary

		del data['bills'][i][bill_id]
	#looping through every bill and each bill is a separate json file 

	return data['bills']

def insert_into_db(data):
	'''
	Input: data (list) list of dictionaries of bill info and voting records
	Inserts records into corresponding collection in mongodb
	'''
	client = MongoClient()
	db = client.congress
	coll = db.Bills114
	coll.insert(data)

if __name__ == '__main__':
	congress = str(sys.argv[1])
	data = get_votes_data(congress)
	insert_into_db(data)