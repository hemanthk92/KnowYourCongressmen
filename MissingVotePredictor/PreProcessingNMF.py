from pymongo import MongoClient
import json
import numpy as np
import pandas as pd
import graphlab
from sklearn.cross_validation import KFold
from sklearn.metrics import accuracy_score

def voting_data_file():
	'''
	Retrives all voting records of all bills in 114 congress and places them in a csv file
	'''
	client = MongoClient()
	db = client.congress
	bills_collection = 'Bills114'

	category = [0,1,2,3,4,5]
	pipe = [{'$match': {'category': {'$in': category}}}, {'$group':{ '_id': "$related_bill__display_number", \
	                            'Date': {'$max': "$created"} }},  {'$project': {'_id':0, 'Date': 1} }]

	data = list(db[bills_collection].aggregate(pipeline=pipe))
	dates = [dictionary['Date'] for dictionary in data]
	bills = list(db[bills_collection].find({'created': {'$in': dates}}, \
	        {'related_bill__display_number': 1, 'id': 1, 'vote_voter': 1, 'link': 1}))


	map_values = {'Yea': 2, 'Aye': 2, 'No': 1, 'Nay': 1, 'Present': 0, 'Not Voting': 0}

	with open('data/VotingRecords/table114.data', 'w') as f:
		for bill_index in xrange(len(bills)):
			bill_id = bills[bill_index]['id']
			link = bills[bill_index]['link']
			for person, vote in bills[bill_index]['vote_voter'].iteritems(): 
				vote_value = map_values[vote]
				if vote_value != 0:
					f.write('%d, %sklearn, %d, %s \n' %(bill_id, person.encode('ascii', 'ignore'), vote_value, link))

def get_data():
	'''
	Creates an sFrame from csv file created in function above
	'''
	df = pd.read_table('data/VotingRecords/table114.data', sep = ',', names=["bill", "member", "vote", "link"])
	df['bill'] = df['bill'].astype(str)
	df['member'] = df['member'].astype(str)
	df['link'] = df['link'].astype(str)
	return graphlab.SFrame(df[['bill', 'member', 'vote']]) 

def NMF_Testing(sf):
	'''
	Input sf (sFrame) sFrame of voting data for matrix factorization
	Function that does Kfold Cross Validation to optimize NMF for prediction. 
	'''
	kf = KFold(len(df), 6, shuffle=True)
	acc_score = []
	index = 0
	num_latent_features = [1,5,10,15,20,25]
	for train_index, test_index in kf:
		df_subset = df.ix[train_index]
		sf = graphlab.SFrame(df_subset)
		df_test = df.ix[test_index]
		sf_test = graphlab.SFrame(df_test)
		rec = graphlab.recommender.factorization_recommender.create(
						sf,
						num_factors = num_latent_features[index],
						user_id='member',
						item_id='bill',
						target='vote',
						solver='als',
						side_data_factorization=False)

		predictions =  rec.predict(sf_test)
		y_p = [round(i) for i in predictions]
		acc_score.append(accuracy_score(y_p, df_test.vote))
		index = index + 1

	plt.plot(num_latent_features, acc_score, '--o')

def vote_to_value(x):
    if x >= 2:
        return 'Yea'
    else:
        return 'No'

def NMF_Prediction(sf):
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
	voting_data_file()
	sf = get_data()
	NMF_Testing(sf)
	NMF_Prediction(sf)



