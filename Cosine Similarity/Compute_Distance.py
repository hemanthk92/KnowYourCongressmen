from mat_gen import Voting_Matrix 
import numpy as np
import pandas as pd 
from scipy.stats import mode 
from scipy.spatial.distance import pdist, squareform, cosine

def compute_distance():
	'''
	Computes distances between congress members for a particular category and writes out the results
	in a text file. Web App reads these text files to show graphs. 
	'''

	category_map = {1: 'Health_Care', 2: 'National_Security', 3:'Economy', 4:'Domestic Issues'}
	vm = Voting_Matrix('114')
	
	for j in xrange(5):
		votes, member_to_row, name_to_memberid =  vm.generate_matrix(category = [j])
		y = pdist(votes, 'cosine')
		y_dist = squareform(y)
		normed_distances = np.zeros((len(y_dist), len(y_dist)))
		for i in xrange(len(y_dist)):
			min_value = min(y_dist[i,:])
			max_value = max(y_dist[i,:])
			normed_distances[i,:] = (y_dist[i,:]-min_value) / (max_value-min_value)

		np.savetxt("%s_114Distance.csv" %category_map[j], normed_distances, delimiter=",")

if __name__ == '__main__':
	compute_distance()