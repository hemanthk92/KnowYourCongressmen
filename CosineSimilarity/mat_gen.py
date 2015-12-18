import json
import pandas as pd
import numpy as np 
import sys 
from pymongo import MongoClient

class Voting_Matrix(object):

	def __init__(self, congress):
		'''
		Input: congress: (string) string that specifies which congress to extract voting records from 

		Creating of a Voting Matrix class for a specific congress. 
		'''

		self.congress = congress
		self.map_values = {'Yea': 1, 'Aye': 1, 'No': -1, 'Nay': -1, 'Present': 0, 'Not Voting': 0}

	def load_data(self, category):
		'''
		Input: category (list) from generate_matrix function, specific which bills to extract voting records from 
		
		Queries the database for the bill/voting data. Places it in a list. 
		Queries the databse for congress member information and places it in a list. 

		Output: bills (list) List of dictionaries containing the votes, bill id and bill display number
				members: (list) List of dictionaries containing the congressional member's id, bioguide id and name
		'''

		client = MongoClient()
		db = client.congress

		bills_collection =  'Bills' + self.congress

		pipe = [{'$match': {'category': {'$in': category}}}, {'$group':{ '_id': "$related_bill__display_number", \
									'Date': {'$max': "$created"} }},  {'$project': {'_id':0, 'Date': 1} }]

		data = list(db[bills_collection].aggregate(pipeline=pipe))
		dates = [dictionary['Date'] for dictionary in data]
		bills = list(db[bills_collection].find({'created': {'$in': dates}}, \
				{'related_bill__display_number': 1, 'id': 1, 'vote_voter': 1}))
		

		members_collection = 'Members' + self.congress
		members = list(db[members_collection].find({}, {'person__id': 1, 'person__bioguideid': 1, 'person__name': 1, 'state': 1, 'party': 1}))
		

		return bills, members

	def generate_matrix(self, category=[0,1,2,3,4,5]):
		'''
		Input: category: (list) taken from the user on the web app. Specifies which bills to extract from the database

		Function that loads the data from the category/categories specified by the user using the load_data function. 
		Generates the voting matrix by calling the fill_in_matrix function. 

		Output: votes: (array) array of matrix voting records 
				member_to_row: (dictionary) mapping from a congress member's id to their corresponding row in the voting matrix 
				name_to_memberid: (dictionary) mapping a congressmen's name (as selected in the WebApp) to the id in database 
		'''
		bills, members = self.load_data(category)

		member_to_row = dict()
		for index, dictionary in enumerate(members):
			person__id = str(dictionary['person__id'])
			member_to_row[person__id] = index
		#member_to_row dictionary that maps each member to what row it belongs in the matrix and other member information

		#row_to_member = dict(zip(member_to_row.values(), member_to_row.keys()))
		
		votes = self.fill_in_matrix(bills, member_to_row)

		return votes, member_to_row

	def fill_in_matrix(self, bills, member_to_row):
		'''
		Input: bills (list) List of dictionaries containing the votes, bill id and bill display number
				members (list) List of dictionaries containing the congressional member's id, bioguide id and name
		Output: votes (array) matrix of voting records 
		'''
		
		votes = np.zeros((len(member_to_row), len(bills)))
		#empty matrix of votes that will be filled in the next loop

		for i in xrange(len(bills)):
			for person, vote_value in bills[i]['vote_voter'].iteritems():
				if person in member_to_row.keys():
					vote = self.map_values[vote_value]
					votes[member_to_row[str(person)], i] = vote

		return votes 