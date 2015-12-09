import pandas as pd
import numpy as np
from math import isnan
from collections import Counter
from nltk.stem.snowball import SnowballStemmer
import sys 

def label_bills(congress):
	'''
	Input: Congress: (string) string that specifies which congress to categorize the bill text from
	
	Function that takes the bill text and categorizes the bill into one of 5 categories. The function tokenizes
	and lemmitaizes the entire bill text and then finds which category of words it has the most words in. 

	Output: df: (DataFrame) dataframe that contains the bill id, bill display number and category of 
	every bill. 

	'''

	df = pd.read_csv('data/%s_Bill_text.csv' %congress)

	Health_Care = ['obamacare', 'care', 'health insurance', 'medicare', 'medicad', 'health']
	National_Security = ['terrorism', 'Jihad', 'defense', 'military', 'weapons', 'military', 'international', 'diplomacy', 'security', 'veterns', 'forces']
	Economy = ['taxes', 'jobs', 'banks', 'economy', 'economy', 'costs', 'finance', 'debt', 'economic', 'economical', 'trade', 'finance', 'labor']
	Environment = ['keystone xl', 'environment', 'gas', 'oil', 'renewable', 'energy', 'solar', 'environment', 'transportation', 'natural', 'science', 'land', 'environmental']
	Domestic_Issues = ['civil', 'minority', 'indians', 'race', 'crime', 'community']
	#lists of category identifier terms 

	snowball = SnowballStemmer('english')
	#using SnowballStemmer to lemmitaize and tokenize words 

	Health_Care = [snowball.stem(word)for word in Health_Care]
	National_Security = [snowball.stem(word)for word in National_Security]
	Economy = [snowball.stem(word)for word in Economy]
	Environment = [snowball.stem(word)for word in Environment]
	Domestic_Issues = [snowball.stem(word) for word in Domestic_Issues]

	category_labels = []
	for i in xrange(len(df)):

		if type(df.text[i]) != type(np.nan):
			counts_by_category =np.zeros(6)

		words = [snowball.stem(word) for word in df.text[i].split(' ')]
		for word in words:
			word = word.lower()
			if word in Health_Care:
				counts_by_category[1] +=1
			if word in National_Security:
				counts_by_category[2] +=1
			if word in Economy:
				counts_by_category[3] +=1
			if word in Environment:
				counts_by_category[4] +=1
			if word in Domestic_Issues:
				counts_by_category[5] +=1
			category_labels.append(np.argmax(counts_by_category))
		else:
			category_labels.append(0)

	df['Category'] =  np.array(category_labels)

	return df 


def update_database(df):
	'''
	Input: df: (DataFrame) dataframe that contains the bill id, bill display number and category of 
	every bill. 

	Function that updates the category of every bill in the database 
	'''
	client = MongoClient()
	db = client.Congress 
	for i in xrange(len(df)):
	    db.Bills114_alternate.update_many({"related_bill__display_number": df.display_number[i]}, {"$set": {"category": df.Categ



if __name__ == '__main__':
	congress = str(sys.argv[1])
	df = label_bills(congress)
	update_database(df)


