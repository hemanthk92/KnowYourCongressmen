from pymongo import MongoClient
import json
import numpy as np
import pandas as pd
import graphlab
from PreProcessingNMF import get_data

def prediction(sf):
	'''
	Input sf (sFrame) sFrame of all voting data
	Function that creates an NMF and predicts all the missing votes and then writes out answer to a file. 
	'''
	rec = graphlab.recommender.factorization_recommender.create(
        sf,
        num_factors = 7,
        user_id='member',
        item_id='bill',
        target='vote',
        solver='als',
        side_data_factorization=False)

	unique_bills = set(df.bill)
	unique_links = set(df.link)
	bills_not_voted = []
	member_ids = []
	links_not_voted = []
	for member in set(df.member):
		df_user = df[df['member']==member][['bill', 'member', 'link']]
		#all the bills that the member has voted on
		user_bills_not_voted = list(set(unique_bills) - set(df_user.bill))
		#all the bills the member has not voted on
		bills_not_voted_df = df[df['bill'].isin(user_bills_not_voted)][['link', 'bill']].drop_duplicates()
		#df of bills that havent been voted on
		bills_not_voted.extend(bills_not_voted_df.bill.tolist())
		member_ids.extend([member for i in xrange(len(user_bills_not_voted))])
		links_not_voted.extend([link for link in bills_not_voted_df.link])

	sf_test = graphlab.SFrame(data = {'member': member_ids, 'bill': bills_not_voted})
	pred_in_numbers = [round(value) for value in rec.predict(sf_test)]
	pred = map(vote_to_value, pred_in_numbers)

	with open('nmf_114predictions.csv', 'w') as f:
    	for i in xrange(len(pred)):
        	f.write('%s,%s,%s,%s\n' %(member_ids[i], bills_not_voted[i], links_not_voted[i], pred[i]))

if __name__ == '__main__':
	sf = get_data()
	prediction(sf)