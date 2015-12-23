from mat_gen import Voting_Matrix 
import numpy as np
import pandas as pd 
from scipy.stats import mode 
from scipy.spatial.distance import pdist, squareform, cosine
import json

def compute_distance():
	'''
	Computes distances between congress members for a particular category and writes out the results
	in a text file. Web App reads these text files to show graphs. 
	'''

	category_map = {1: 'Health Care', 2: 'National Security', 3:'Economy', 4:'Environment', 5:'Domestic Issues' }
	vm = Voting_Matrix('114')

	for j in xrange(1,6):
		votes, member_to_row =  vm.generate_matrix(category = [j])
		y = pdist(votes, 'cosine')
		y_dist = squareform(y)
		normed_distances = np.zeros((len(y_dist), len(y_dist)))
		for i in xrange(len(y_dist)):
			min_value = min(y_dist[i,:])
			max_value = max(y_dist[i,:])
			normed_distances[i,:] = (y_dist[i,:]-min_value) / (max_value-min_value)

		np.savetxt("data/%s114Distance.csv" %category_map[j], normed_distances, delimiter=",", fmt='%5.5f')

	votes, member_to_row =  vm.generate_matrix(category = [1,2,3,4,5])
	y = pdist(votes, 'cosine')
	y_dist = squareform(y)
	normed_distances = np.zeros((len(y_dist), len(y_dist)))
	for i in xrange(len(y_dist)):
		min_value = min(y_dist[i,:])
		max_value = max(y_dist[i,:])
		normed_distances[i,:] = (y_dist[i,:]-min_value) / (max_value-min_value)
	np.savetxt("data/All Categories114Distance.csv" , normed_distances, delimiter=",", fmt='%5.5f')

	df = pd.read_csv('../DataCollectionInsertion/Members/114Members.csv')
	row_nums = np.array([member_to_row[str(df.iloc[i]['person__id'])] for i in xrange(len(df))])
	df['row_nums'] = row_nums
	df.to_csv('../DataCollectionInsertion/Members/114Members.csv', sep=',')

if __name__ == '__main__':
	compute_distance()