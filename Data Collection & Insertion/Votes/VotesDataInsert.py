from pymongo import MongoClient
import json
from os.path import isfile, join
from os import listdir
import pandas as pd
import json 
import numpy


def get_votes_data():
	'''
	Retrieves bill information and voting records from files. Filters the columns and rows
	Output: data['bills'] list of dictionaries of bill info and voting records
	'''
	df = pd.read_csv('../data/Raw_Data/%s_bills_ids.csv' %congress)
	with open('../data/Raw_Data/%s_votes.json' %congress) as dataf:
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
	db = client.Congress
	coll.inset(data)

if __name__ == '__main__':
	data = get_votes_data()
	insert_into_db(data)