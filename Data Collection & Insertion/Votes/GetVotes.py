import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import sys
import threading
from timeit import Timer
import json 
import time

def get_bill_ids(congress):
	'''
	Input: congress (string) string that specifies which congress to fetch bill ids from 
	
	This function makes an API request to extract the bills from a particular congress.  

	Output: df_votes (dataframe) dataframe of every bill that has been voted on in particular congress 
	and assoicated bill information.  
	'''

	df_votes = pd.read_csv('https://www.govtrack.us/api/v2/vote?congress__in=' +  congress + \
			'&chamber=house&fields=id,related_bill__display_number,created,result,question,required, \
			total_minus,total_other,total_plus,vote_type,session,margin,category,link&format=csv&limit=5900')
	#loading the bill id's of all bills in the 114th House
	return df_votes

def generate_api_calls(bills_ids):
	'''
	Input: bills_ids (list) list of bills ids 

	This function creates the string for API calls. This API calls find the voting records of all members for a subset 
	of bills. 

	Output: bills_ids_subsets (list): a list of list, with each list having 14 bill ids
			api_queries (list): a list of api queries 
	'''
	bills_ids = map(str, bills_ids)
	bills_ids_subsets = []
	api_queries = []
	count = 0
	for i in xrange(len(bills_ids)/14):
		bills_ids_subsets.append(bills_ids[i*14:(i*14)+14])
		api_queries.append('https://www.govtrack.us/api/v2/vote_voter?vote__in=' +'|'.join(bills_ids[i*14:(i*14)+14])+ '&fields=option__value,person__id,vote__id&format=csv&limit=5999')
		count += 1
	#bills_ids_subsets is a list of list, with each list having 14 bill ids, 
	#each subset of bills ids is translated into its corresponding api script. 
	
	if count*14 < len(bills_ids):
		bills_ids_subsets.append(bills_ids[count*14:len(bills_ids)])
		api_queries.append('https://www.govtrack.us/api/v2/vote_voter?vote__in=' + '|'.join(bills_ids[count*14:len(bills_ids)]) + '&fields=option__value,person__id,vote__id&format=csv&limit=5999')
	return bills_ids_subsets, api_queries



def request(bills_ids_subsets, api_queries, congress):
	'''
	Input: congress (string): string to label file name 
		   bills_ids_subsets (list): a list of list, with each list having 14 bill ids
		   api_queries (list): a list of api queries 
	
	Output: final_bills_ids (list) a list of bill ids whose corresponding voting records will be put in the database 
	'''
	final_bills_ids = []
	
	with open('../data/%s_votes.json' %congress, 'w') as fp:

		base_dict = dict()
		base_dict['bills'] = []	

		for index in xrange(len(api_queries)):
			
			df = pd.read_csv(api_queries[index])
			time.sleep(1)

			for _id in bills_ids_subsets[index]:
				
				temp = df[df['vote__id'] == int(_id)]

				if set(temp['option__value'].unique().tolist()) == set(['Present', 'Not Voting']):
					continue
				elif len([value for value in temp['option__value'].unique().tolist() if value not in ['Aye', 'Nay', 'No', 'Yea', 'Not Voting', 'Present']]) > 0:
					continue
			
				d = dict()
				d[_id] = dict(zip(temp['person__id'].tolist(), temp['option__value'].tolist()))
				base_dict['bills'].append(d)
				final_bills_ids.append(_id) 
		json.dump(base_dict, fp)

	return final_bills_ids

def write_file(df_congress, final_bills_ids, congress):
	'''
	Input: df_congress (dataframe) dataframe of every bill that has been voted on in particular congress 
	and assoicated bill information.  
	final_bills_ids (list): a list of bill ids whose corresponding voting records will be put in the database 
	congress (string) string for filename 

	Function that writes the final bills ids and assoicated info from df_congress to a file 
	'''
	final_bills_ids = map(int, final_bills_ids)
	df_congress = df_congress[df_congress['id'].isin(final_bills_ids)]
	df_congress.to_csv('../data/%s_bills_ids.csv' %congress)

def generate_files(congress):
	'''
	Input: congress (string) identifier for which congress to get data from 

	Function that calls all other functions in the file
	'''
	congress = str(congress)
	df_congress = get_bill_ids(congress)
	bills_ids = list(df_congress['id'])
	bills_ids_subsets, api_queries = generate_api_calls(bills_ids)
	final_bills_ids = request(bills_ids_subsets, api_queries, congress)
	write_file(df_congress, final_bills_ids, congress)

if __name__ == '__main__':
	congress = str(sys.argv[1])
	generate_files(congress)
	