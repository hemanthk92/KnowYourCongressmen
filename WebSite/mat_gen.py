import json
import pandas as pd
import numpy as np 
import sys 
from pymongo import MongoClient

class Voting_Matrix(object):

	def __init__(self, congress):

		self.congress = congress
		self.map_values = {'Yea': 1, 'Aye': 1, 'No': -1, 'Nay': -1, 'Present': 0, 'Not Voting': 0}

	def load_data(self, category):
		client = MongoClient()
		db = client.Congress

		bills_collection =  'Bills' + self.congress

		pipe = [{'$match': {'category': {'$in': category}}}, {'$group':{ '_id': "$related_bill__display_number", \
									'Date': {'$max': "$created"} }},  {'$project': {'_id':0, 'Date': 1} }]

		data = list(db[bills_collection].aggregate(pipeline=pipe))
		dates = [dictionary['Date'] for dictionary in data]
		bills = list(db[bills_collection].find({'created': {'$in': dates}}, \
				{'related_bill__display_number': 1, 'id': 1, 'vote_voter': 1}))
		#List of dictionaries containing the votes, bill id and bill display number

		members_collection = 'Members' + self.congress
		members = list(db[members_collection].find({}, {'person__id': 1, 'person__bioguideid': 1, 'person__name': 1, 'state': 1, 'party': 1}))
		#List of dictionaries containing the congressional member's id, bioguide id and name

		return bills, members

	def generate_matrix(self, category=[0,1,2,3,4,5]):
		bills, members = self.load_data(category)

		member_to_row = dict()
		for index, dictionary in enumerate(members):
			person__id = str(dictionary['person__id'])
			member_to_row[person__id] = [index, dictionary['person__name'].encode('ascii', 'ignore'), \
						dictionary['state'].encode('ascii', 'ignore'), dictionary['party'].encode('ascii', 'ignore')]
		#member_to_row dictionary that maps each member to what row it belongs in the matrix and other member information

		name_to_memberid = dict(zip([member[1] for member in member_to_row.values()] , member_to_row.keys()))
		
		votes = self.fill_in_matrix(bills, member_to_row)

		return votes, member_to_row, name_to_memberid

	def fill_in_matrix(self, bills, member_to_row):
		
		votes = np.zeros((len(member_to_row), len(bills)))
		#empty matrix of votes that will be filled in the next function

		for i in xrange(len(bills)):
			for person, vote_value in bills[i]['vote_voter'].iteritems():
				if person in member_to_row.keys():
					vote = self.map_values[vote_value]
					votes[member_to_row[str(person)][0], i] = vote

		return votes 