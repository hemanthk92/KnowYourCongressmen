import pandas as pd
from pymongo import MongoClient
import json
from os.path import isfile, join
from os import listdir

def get_members_data():
	'''
	Makes an API request to the GovTrack API to get all congressional members. Stores results in dataframe. 
	Output: (list) list of dictionaries that has member information
	'''

	enddate = '20170103'
	states = pd.read_csv('../data/states.csv')
	states = states['Abbreviation'].tolist()

	df = pd.read_csv('https://www.govtrack.us/api/v2/role?enddate=' + enddate + '&fields=district,enddate,leadership_title,party,person__bioguideid,gender,person__id,person__name,role_type,state,title&format=csv&limit=6000')
	df_reps = df[df['role_type']=='representative']
	df_reps['person__name'] = df_reps['person__name'].map(lambda x: x.split('[')[0])
	df_reps['person__name'] = df_reps['person__name'].map(lambda x: x[:len(x)-1])
	df_reps = df_reps[df_reps['state'].isin(states)] 
	#splitting name string to remove district number
	df_reps.to_csv('114Members.csv', sep=',')
	return df_reps.T.to_dict().values()

def insert_into_db(data):
	'''
	Input: (list) list of dictionaries to be inserted into database
	Inserts records into corresponding collection in mongodb
	'''

	client = MongoClient()
	db = client.congress
	coll = db.Members114
	coll.insert(data)

if __name__ == '__main__':
	data = get_members_data()
	#insert_into_db(data)