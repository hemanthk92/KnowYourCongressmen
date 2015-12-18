import pandas as pd 
import requests
import bs4
from pymongo import MongoClient
import sys
import numpy as np 
import json 

def get_display_numbers(congress):
	'''
	Input: congress (string) specifies which session to extract bill text from 

	This function queries the database for the bills and their associated information for a particular congress.

	Output: bill_display_numbers (list) list of bill display numbers (ex. H. Res 5, etc).
									bill display numbers are not unique for each bill, 
			bill_ids (list) list of bill ids 
	'''
	
	client = MongoClient()
	db = client.congress 

	collection_name = 'Bills' + str(congress)
	pipe =[{'$group':{'_id': "$related_bill__display_number", 'value': {'$max': "$id"} }}]
	data = list(db[collection_name].aggregate(pipeline=pipe))
	
	bill_display_numbers = [element['_id'] for element in data if type(element['_id']) != type(np.nan)]
	bill_ids = [element['value'] for element in data if type(element['_id']) != type(np.nan)]
	
	return bill_display_numbers, bill_ids

formatter = {
    'H.Res.': 'HE',
    'H.R.': 'HR',
    'S.': 'SN',
    'H.J.Res.': 'SN',
    'S.J.Res.': 'SJ',
    'H.Con.Res.': 'HC',
    'S.Con.Res.': 'SC'
}

def form_urls(bill_display_numbers):
	'''
	Input: bill_display_numbers (list) list of bill display numbers 

	This function forms the urls that are needed for the web scarping of the text. 

	Output: urls (list) list of urls that have the bill text associated with a bill display number  
	'''

	urls = ['http://thomas.loc.gov/cgi-bin/bdquery/z?d114:' + formatter[bill.split(' ')[0]] \
		+ bill.split(' ')[1].zfill(5) + ':@@@D&summ2=m&' for bill in bill_display_numbers]
	return urls 

def get_text(urls, bill_display_numbers, congress, bill_ids):
	'''
	Input: urls (list) list of urls of the bill texts 
		   bill_display_numbers (list) list of bill display numbers 
		   congress (string) congress number string
		   bill_ids (list) list of ids of every bill

	This function scraps every url in the urls list and extracts the bill text.
	It then places the bill text in a csv file. 
	'''

	with open("../data/%s_Bill_text.csv" %congress, "w") as f:
	
		for index in xrange(len(urls)):
			html = requests.get(urls[index]).content
			soup = bs4.BeautifulSoup(html, 'html.parser')
			bill_descriptions = [subject['content'].replace('\n', '').encode('ascii', 'ignore') for subject in soup.findAll("meta", {"name": "dc.subject"})]
			text = ' '.join(bill_descriptions).replace(',', '')
			f.write(bill_display_numbers[index] + ',' + str(bill_ids[index]) + ',' + text + '\n')
	

if __name__ == '__main__':
	congress = str(sys.argv[1])
	bill_display_numbers, bill_ids = get_display_numbers(congress)
	urls = form_urls(bill_display_numbers) 
	get_text(urls, bill_display_numbers, congress, bill_ids)